from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

import numpy as np

from src.utils.klines import has_first_historical_kline
from src.utils.klines import has_realtime_kline
from src.infrastructure.db import DBManager

if TYPE_CHECKING:
    from src.infrastructure.clients.exchanges.binance import BinanceClient
    from src.infrastructure.clients.exchanges.bybit import BybitClient


class HistoryProvider():
    """
    Provides historical market data (klines, precisions) from exchanges
    (Binance, Bybit) with local database caching functionality.
    
    Handles:
    - Fetching price/quantity precisions with local caching
    - Fetching klines data with smart local database management
    - Optional additional data feeds
    """

    def __init__(self) -> None:
        """
        Initializes the HistoryProvider with DBManager instance and logger.
        """

        self.db_manager = DBManager()
        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
        start: str,
        end: str,
        feeds: dict | None
    ) -> dict:
        """
        Fetches complete market data package including
        klines, precisions and optional feeds.
        
        Args:
            client: Exchange API client (Binance/Bybit)
            symbol: Trading symbol (e.g. 'BTCUSDT')
            interval: Kline interval (str or int)
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format
            feeds: Optional additional data feeds configuration
            
        Returns:
            dict: Complete market data package including:
                - Market metadata
                - Price/quantity precisions
                - Klines data
                - Additional feeds if requested
        """
        
        p_precision, q_precision = self._fetch_precisions(client, symbol)

        valid_interval = client.get_valid_interval(interval)
        klines = self._fetch_klines(
            client=client,
            symbol=symbol,
            interval=valid_interval,
            start=start,
            end=end
        )

        additional_data = self._fetch_additional_data(
            client=client,
            symbol=symbol,
            start=start,
            end=end,
            feeds=feeds
        ) if feeds else {'feeds': {}}

        result = {
            'symbol': symbol,
            'interval': valid_interval,
            'start': start,
            'end': end,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            **additional_data
        }

        return result

    def _fetch_precisions(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
    ) -> tuple[float, float]:
        """
        Fetches price and quantity precisions for a symbol
        with local database caching.
        
        Args:
            client: Exchange API client
            symbol: Trading symbol
            
        Returns:
            tuple: (price_precision, quantity_precision)
        """

        database_name = f'{client.EXCHANGE.lower()}.db'
        precision_data = self.db_manager.fetch_one(
            database_name=database_name,
            table_name='symbol_precisions',
            key_column='symbol',
            key_value=symbol
        )

        if precision_data:
            p_precision = precision_data[1]
            q_precision = precision_data[2]
        else:
            p_precision = client.get_price_precision(symbol)
            q_precision = client.get_qty_precision(symbol)

            if p_precision is not None and q_precision is not None:
                self.db_manager.save(
                    database_name=database_name,
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

    def _fetch_klines(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str,
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

        request_required = False

        database_name = f'{client.EXCHANGE.lower()}.db'
        table_name = f'{symbol}_{interval}'

        start_ms = int(
            datetime.strptime(start, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        end_ms = int(
            datetime.strptime(end, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        start_to_request_ms = start_ms
        end_to_request_ms = end_ms

        klines = self.db_manager.fetch_all(database_name, table_name)

        if not klines or len(klines) < 2:
            request_required = True

        if not request_required and start_ms < klines[0][0]:
            first_kline = self.db_manager.fetch_one(
                database_name=database_name,
                table_name='klines_metadata',
                key_column='klines_key',
                key_value=table_name
            )

            if not first_kline:
                end_to_request_ms = max(end_ms, klines[-1][0])
                request_required = True

        if not request_required and end_ms > klines[-1][0]:
            kline_ms = klines[1][0] - klines[0][0]
            now_ms = int(datetime.now().timestamp() * 1000)
            end_to_request_ms = min(end_ms, now_ms - kline_ms)

            if bool((end_to_request_ms - klines[-1][0]) // kline_ms):
                start_to_request_ms = min(start_ms, klines[0][0])
                request_required = True

        if request_required:
            klines = self._fetch_klines_from_exchange(
                client=client,
                symbol=symbol,
                interval=interval,
                start=start_to_request_ms,
                end=end_to_request_ms
            )

            if has_realtime_kline(klines):
                klines = klines[:-1]

            self.db_manager.save(
                database_name=database_name,
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

            if has_first_historical_kline(klines, start_ms):
                self.db_manager.save(
                    database_name=database_name,
                    table_name='klines_metadata',
                    columns={
                        'klines_key': 'TEXT PRIMARY KEY',
                        'has_first_kline': 'BOOLEAN'
                    },
                    rows=[[table_name, True]],
                    drop=False
                )

        klines = np.array(klines)
        klines = klines[
            (klines[:, 0] >= start_ms) &
            (klines[:, 0] <= end_ms)
        ]

        if klines.size == 0:
            start_str = (
                datetime.fromtimestamp(start_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No klines available | '
                f'{client.EXCHANGE} | '
                f'{symbol} | '
                f'{interval} | '
                f'{start_str} → {end_str}'
            )
        
        return klines

    def _fetch_klines_from_exchange(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str,
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
            f'Requesting klines | '
            f'{client.EXCHANGE} | '
            f'{symbol} | '
            f'{interval}'
        )

        klines = client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        if not klines:
            start_str = (
                datetime.fromtimestamp(start / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No klines available | Period: {start_str} → {end_str}'
            )

        return [
            [float(value) for value in kline[:6]]
            for kline in klines
        ]

    def _fetch_additional_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        start: str,
        end: str,
        feeds: dict
    ) -> dict:
        """
        Fetches additional data feeds specified in the configuration.
        
        Currently supports:
        - Secondary klines feeds with different symbols/intervals
            
        Args:
            client: Exchange API client
            symbol: Base trading symbol
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format
            feeds: Feeds configuration dictionary
            
        Returns:
            dict: Dictionary containing all requested additional feeds
        """

        result = {}

        if 'klines' in feeds:
            klines_data = {}

            for feed_name, feed_config in feeds['klines'].items():
                feed_symbol = (
                    symbol if feed_config[0] == 'symbol' else feed_config[0]
                )
                feed_interval = feed_config[1]

                klines_data[feed_name] = self._fetch_klines(
                    client=client,
                    symbol=feed_symbol,
                    interval=feed_interval,
                    start=start,
                    end=end
                )
            
            if klines_data:
                result['feeds'] = {'klines': klines_data}
        
        return result