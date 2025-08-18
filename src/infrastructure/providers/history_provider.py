from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

import numpy as np

from src.core.quantklines import shrink, stretch
from src.utils.klines import has_first_historical_kline
from src.utils.klines import has_realtime_kline
from src.infrastructure.db import DBManager

if TYPE_CHECKING:
    from src.infrastructure.clients.exchanges.binance import BinanceClient
    from src.infrastructure.clients.exchanges.bybit import BybitClient


class HistoryProvider():
    """
    Provides historical market data from exchanges
    with local database caching functionality.
    
    Responsibilities:
        - Fetch price/quantity precisions with local caching
        - Fetch klines with database-aware management
        - Optionally fetch additional synchronized feeds
    """

    def __init__(self) -> None:
        """
        Initializes the HistoryProvider with DBManager instance and logger.
        """

        self.db_manager = DBManager()
        self.logger = getLogger(__name__)

    def get_market_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
        start: str,
        end: str,
        feeds: dict | None
    ) -> dict:
        """
        Fetches complete market data package:
          - klines
          - price/quantity precisions
          - optional additional feeds
        
        Args:
            client: Exchange API client
            symbol: Trading symbol
            interval: Kline interval
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format
            feeds: Optional feeds config
            
        Returns:
            dict with:
                - symbol, interval, start, end
                - precisions
                - klines
                - feeds (if requested)
        """
        
        p_precision, q_precision = self._get_precisions(client, symbol)
        valid_interval = client.get_valid_interval(interval)

        klines = self._get_klines(
            client=client,
            symbol=symbol,
            interval=valid_interval,
            start=start,
            end=end
        )

        feeds_data = (
            self._get_feeds_data(
                client=client,
                symbol=symbol,
                feeds=feeds,
                main_interval=valid_interval,
                main_klines=klines,
                start=start,
                end=end
            )
            if feeds
            else {'feeds': {}}
        )

        return {
            'symbol': symbol,
            'interval': valid_interval,
            'start': start,
            'end': end,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            **feeds_data
        }

    def _get_precisions(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
    ) -> tuple[float, float]:
        """
        Get price and quantity precisions for a symbol.
        
        Args:
            client: Exchange API client
            symbol: Trading symbol
            
        Returns:
            tuple: (price_precision, quantity_precision)
        """

        db_name = f'{client.EXCHANGE.lower()}.db'
        precision_data = self.db_manager.fetch_one(
            database_name=db_name,
            table_name='symbol_precisions',
            key_column='symbol',
            key_value=symbol
        )

        if precision_data:
            return precision_data[1], precision_data[2]

        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)

        if p_precision is not None and q_precision is not None:
            self.db_manager.save(
                database_name=db_name,
                table_name='symbol_precisions',
                columns={
                    'symbol': 'TEXT PRIMARY KEY',
                    'price_precision': 'REAL',
                    'qty_precision': 'REAL'
                },
                rows=[[symbol, p_precision, q_precision]],
                drop=False
            )

        return p_precision, q_precision

    def _get_klines(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
        start: str,
        end: str
    ) -> np.ndarray:
        """
        Smart klines fetcher with local database management.

        Implements:
        - Database caching
        - Automatic gap filling
        - Real-time kline validation
        - Date range filtering

        Args:
            client: Exchange API client
            symbol: Trading symbol
            interval: Kline interval
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format

        Returns:
            np.ndarray: Array of klines data

        Raises:
            ValueError: If no klines available for requested period
        """

        db_name = f'{client.EXCHANGE.lower()}.db'
        table_name = f'{symbol}_{interval}'

        start_ms = self._to_ms(start)
        end_ms = self._to_ms(end)
        request_required = False
        start_req, end_req = start_ms, end_ms

        raw_klines = self.db_manager.fetch_all(db_name, table_name)

        if not raw_klines or len(raw_klines) < 2:
            request_required = True
        elif start_ms < raw_klines[0][0]:
            first_meta = self.db_manager.fetch_one(
                database_name=db_name,
                table_name='klines_metadata',
                key_column='klines_key',
                key_value=table_name
            )

            if not first_meta:
                end_req = max(end_ms, raw_klines[-1][0])
                request_required = True

        if not request_required and end_ms > raw_klines[-1][0]:
            kline_ms = raw_klines[1][0] - raw_klines[0][0]
            now_ms = int(datetime.now().timestamp() * 1000)
            end_req = min(end_ms, now_ms - kline_ms)

            if bool((end_req - raw_klines[-1][0]) // kline_ms):
                start_req = min(start_ms, raw_klines[0][0])
                request_required = True

        if request_required:
            raw_klines = self._get_klines_from_exchange(
                client=client,
                symbol=symbol,
                interval=interval,
                start=start_req,
                end=end_req
            )
            klines = np.array(raw_klines)[:, :6].astype(float)

            if has_realtime_kline(klines):
                klines = klines[:-1]

            self.db_manager.save(
                database_name=db_name,
                table_name=table_name,
                columns={
                    'time': 'INTEGER PRIMARY KEY',
                    'open': 'REAL',
                    'high': 'REAL',
                    'low': 'REAL',
                    'close': 'REAL',
                    'volume': 'REAL'
                },
                rows=klines,
                drop=True
            )

            if has_first_historical_kline(raw_klines, start_ms):
                self.db_manager.save(
                    database_name=db_name,
                    table_name='klines_metadata',
                    columns={
                        'klines_key': 'TEXT PRIMARY KEY',
                        'has_first_kline': 'BOOLEAN'
                    },
                    rows=[[table_name, True]],
                    drop=False
                )
        else:
            klines = np.array(raw_klines)

        klines = klines[(klines[:, 0] >= start_ms) & (klines[:, 0] <= end_ms)]

        if klines.size == 0:
            raise ValueError(
                f'No klines available | '
                f'{client.EXCHANGE} | '
                f'{symbol} | '
                f'{interval} | '
                f'{start} → {end}'
            )
        
        return klines

    def _get_klines_from_exchange(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
        start: int,
        end: int
    ) -> list:
        """
        Direct exchange API call for klines data with timestamp conversion.
        
        Args:
            client: Exchange API client
            symbol: Trading symbol
            interval: Kline interval
            start: Start timestamp in milliseconds
            end: End timestamp in milliseconds
            
        Returns:
            list: Raw klines data from exchange
            
        Raises:
            ValueError: If no klines available from exchange
        """
        
        self.logger.info(
            f'Requesting klines | {client.EXCHANGE} | '
            f'{symbol} | {interval}'
        )

        klines = client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        if not klines:
            raise ValueError(
                f'No klines available | Period: '
                f'{self._to_str(start)} → {self._to_str(end)}'
            )

        return [
            [float(value) for value in kline[:6]]
            for kline in klines
        ]

    def _get_feeds_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        feeds: dict,
        main_interval: str | int,
        main_klines: np.ndarray,
        start: str,
        end: str
    ) -> dict:
        """
        Fetch additional data feeds based on configuration.
        
        Currently supports secondary klines feeds with different
        symbols or intervals, resampled to match the main kline array.
            
        Args:
            client: Exchange API client
            symbol: Base trading symbol
            feeds: Configuration dictionary specifying additional feeds
            main_interval: Interval of the main kline array
            main_klines: Main array of klines used as reference for resampling
            start: Start date ('YYYY-MM-DD')
            end: End date ('YYYY-MM-DD')
            
        Returns:
            dict: Requested feeds data, structured as:
                {'feeds': {'klines': {feed_name: np.ndarray, ...}}}
        """

        if 'klines' not in feeds:
            return {}

        klines_by_feed = {}
        for feed_name, feed_config in feeds['klines'].items():
            feed_key, feed_interval_key = feed_config[:2]
            feed_symbol = symbol if feed_key == 'symbol' else feed_key
            feed_interval = client.get_valid_interval(feed_interval_key)

            main_ms = client.INTERVAL_MS[main_interval]
            feed_ms = client.INTERVAL_MS[feed_interval]

            klines = self._get_klines(
                client=client,
                symbol=feed_symbol,
                interval=feed_interval,
                start=start,
                end=end
            )

            if main_ms <= feed_ms:
                klines = stretch(
                    higher_tf_data=klines,
                    higher_tf_time=klines[:, 0],
                    target_tf_time=main_klines[:, 0]
                )
            else:
                klines = shrink(
                    lower_tf_data=klines,
                    lower_tf_time=klines[:, 0],
                    target_tf_time=main_klines[:, 0]
                )

            klines_by_feed[feed_name] = klines
        
        return {'feeds': {'klines': klines_by_feed}}
    
    @staticmethod
    def _to_ms(date_str: str) -> int:
        """
        Convert date string in 'YYYY-MM-DD' format
        to UTC timestamp in milliseconds.
        
        Args:
            date_str: Date string in 'YYYY-MM-DD' format.
        
        Returns:
            int: Corresponding UTC timestamp in milliseconds.
        """

        return int(
            datetime.strptime(date_str, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )

    @staticmethod
    def _to_str(ms: int) -> str:
        """
        Convert UTC timestamp in milliseconds to date string
        in 'YYYY-MM-DD' format.
        
        Args:
            ms: Timestamp in milliseconds (UTC).
        
        Returns:
            str: Date string in 'YYYY-MM-DD' format.
        """

        return datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d')