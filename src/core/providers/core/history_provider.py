from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

import numpy as np

from src.infrastructure.db import db_manager
from src.infrastructure.exchanges.models import Interval
from src.shared.utils import (
    has_first_historical_kline,
    has_realtime_kline
)
from ..common.utils import shrink, stretch

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient
    from ..common.models import MarketData, FeedsData


class HistoryProvider():
    """
    Provides historical market data from exchanges
    with local database caching functionality.
    """

    def get_market_data(
        self,
        client: BaseExchangeClient,
        symbol: str,
        interval: Interval,
        start: str,
        end: str,
        feeds: dict[str, dict[str, Any]]
    ) -> MarketData:
        """
        Fetches complete market data package:
          - klines
          - price/quantity precisions
          - optional additional feeds
        
        Args:
            client: Exchange API client for data fetching
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format
            feeds: Optional feeds config
        
        Returns:
            MarketData: Market data package
        """
        
        p_precision, q_precision = self._get_precisions(client, symbol)

        klines = self._get_klines(
            client=client,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        feeds_data = (
            self._get_feeds_data(
                client=client,
                symbol=symbol,
                feeds=feeds,
                main_interval=interval,
                main_klines=klines,
                start=start,
                end=end
            )
            if feeds and klines.size != 0 else {}
        )

        return {
            'symbol': symbol,
            'interval': interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            'feeds': feeds_data,
            'start': start,
            'end': end,
        }
    
    def _get_precisions(
        self,
        client: BaseExchangeClient,
        symbol: str,
    ) -> tuple[float, float]:
        """
        Get price and quantity precisions for a symbol.
        
        Args:
            client: Exchange API client for data fetching
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            tuple: (price_precision, quantity_precision)
        """

        db_name = f'{client.exchange_name.lower()}.db'
        symbol_key = symbol.lower()

        precision_data = db_manager.fetch_one(
            database_name=db_name,
            table_name='symbol_precisions',
            key_column='symbol',
            key_value=symbol_key
        )

        if precision_data:
            return precision_data[1], precision_data[2]

        p_precision = client.market.get_price_precision(symbol)
        q_precision = client.market.get_qty_precision(symbol)

        if p_precision is not None and q_precision is not None:
            db_manager.insert_one(
                database_name=db_name,
                table_name='symbol_precisions',
                columns={
                    'symbol': 'TEXT PRIMARY KEY',
                    'price_precision': 'REAL',
                    'qty_precision': 'REAL'
                },
                row=(symbol_key, p_precision, q_precision),
                replace=True
            )

        return p_precision, q_precision

    def _get_klines(
        self,
        client: BaseExchangeClient,
        symbol: str,
        interval: Interval,
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
            client: Exchange API client for data fetching
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            start: Start date in 'YYYY-MM-DD' format
            end: End date in 'YYYY-MM-DD' format

        Returns:
            np.ndarray: Array of klines data

        Raises:
            ValueError: If no klines available for requested period
        """

        db_name = f'{client.exchange_name.lower()}.db'
        table_name = f'{symbol}_{interval.name}'.lower()

        start_ms = self._to_ms(start)
        end_ms = self._to_ms(end)
        request_required = False
        start_req, end_req = start_ms, end_ms

        raw_klines = db_manager.fetch_all(db_name, table_name)

        if not raw_klines or len(raw_klines) < 2:
            request_required = True
        elif start_ms < raw_klines[0][0]:
            first_meta = db_manager.fetch_one(
                database_name=db_name,
                table_name='klines_metadata',
                key_column='table_name',
                key_value=table_name.lower()
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

            if not raw_klines:
                return np.array([])
            
            klines = np.array(raw_klines)[:, :6].astype(float)

            if has_realtime_kline(klines):
                klines = klines[:-1]

            db_manager.insert_many(
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
                db_manager.insert_one(
                    database_name=db_name,
                    table_name='klines_metadata',
                    columns={
                        'table_name': 'TEXT PRIMARY KEY',
                        'has_first_kline': 'BOOLEAN'
                    },
                    row=(table_name, True),
                    replace=True
                )
        else:
            klines = np.array(raw_klines)
        
        return klines[(klines[:, 0] >= start_ms) & (klines[:, 0] <= end_ms)]

    def _get_klines_from_exchange(
        self,
        client: BaseExchangeClient,
        symbol: str,
        interval: Interval,
        start: int,
        end: int
    ) -> list[list[float]]:
        """
        Direct exchange API call for klines data with timestamp conversion.
        
        Args:
            client: Exchange API client for data fetching
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            start: Start timestamp in milliseconds
            end: End timestamp in milliseconds
            
        Returns:
            list: Raw klines data from exchange
        """

        klines = client.market.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        if not klines:
            return []
        
        return [
            [float(value) for value in kline[:6]]
            for kline in klines
        ]

    def _get_feeds_data(
        self,
        client: BaseExchangeClient,
        symbol: str,
        feeds: dict[str, dict[str, Any]],
        main_interval: Interval,
        main_klines: np.ndarray,
        start: str,
        end: str
    ) -> FeedsData:
        """
        Fetch additional data feeds based on configuration.
        
        Currently supports secondary klines feeds with different
        symbols or intervals, resampled to match the main kline array.
            
        Args:
            client: Exchange API client for data fetching
            symbol: Base trading symbol
            feeds: Configuration dictionary specifying additional feeds
            main_interval: Interval of the main kline array
            main_klines: Main array of klines
            start: Start date ('YYYY-MM-DD')
            end: End date ('YYYY-MM-DD')
            
        Returns:
            FeedsData: Additional market data feeds package
        """

        if 'klines' not in feeds:
            return {}

        klines_by_feed: dict[str, np.ndarray] = {}
        for feed_name, feed_config in feeds['klines'].items():
            feed_key, feed_interval = feed_config[:2]
            feed_symbol = symbol if feed_key == 'symbol' else feed_key

            main_ms = client.market.get_interval_duration(main_interval)
            feed_ms = client.market.get_interval_duration(feed_interval)

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
        
        return {'klines': klines_by_feed}
    
    @staticmethod
    def _to_ms(date_str: str) -> int:
        """
        Convert date string in 'YYYY-MM-DD' format
        to UTC timestamp in milliseconds.
        
        Args:
            date_str: Date string in 'YYYY-MM-DD' format
        
        Returns:
            int: Corresponding UTC timestamp in milliseconds
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
            ms (int): Timestamp in milliseconds (UTC)
        
        Returns:
            str: Date string in 'YYYY-MM-DD' format
        """

        return datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d')