from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from logging import getLogger
from time import time

from src.infrastructure.exchanges.enums import Interval
from .base import BaseBybitClient


class MarketClient(BaseBybitClient):
    """
    Client for Bybit market data operations.
    
    Handles market data retrieval including klines, tickers,
    symbol information, and precision data.
    """

    _INTERVAL_MAP = {
        Interval.MIN_1: 1,
        Interval.MIN_5: 5,
        Interval.MIN_15: 15,
        Interval.MIN_30: 30,
        Interval.HOUR_1: 60,
        Interval.HOUR_2: 120,
        Interval.HOUR_4: 240,
        Interval.HOUR_6: 360,
        Interval.HOUR_12: 720,
        Interval.DAY_1: 'D',
    }
    _INTERVAL_MS_MAP = {
        Interval.MIN_1: 60000,
        Interval.MIN_5: 300000,
        Interval.MIN_15: 900000,
        Interval.MIN_30: 1800000,
        Interval.HOUR_1: 3600000,
        Interval.HOUR_2: 7200000,
        Interval.HOUR_4: 14400000,
        Interval.HOUR_6: 21600000,
        Interval.HOUR_12: 43200000,
        Interval.DAY_1: 86400000,
    }
    _MAX_WORKERS = 50

    def __init__(self) -> None:
        """Initialize market client with base client functionality."""

        super().__init__()
        self.logger = getLogger(__name__)

    def get_historical_klines(
        self,
        symbol: str,
        interval: Interval,
        start: int,
        end: int
    ) -> list:
        try:
            interval_ms = self.get_interval_duration(interval)
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            return self._fetch_concurrently(symbol, interval, time_ranges)
        except Exception as e:
            self.logger.error(
                f'Failed to request data | Bybit | {symbol} | '
                f'{interval.value} | {type(e).__name__} - {e}'
            )
            return []

    def get_last_klines(
        self,
        symbol: str,
        interval: Interval,
        limit: int = 1000
    ) -> list:
        try:
            if limit <= 1000:
                return self._get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )

            interval_ms = self.get_interval_duration(interval)
            end = int(time() * 1000)
            end = end - (end % interval_ms)
            start = end - interval_ms * limit
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            klines = self._fetch_concurrently(symbol, interval, time_ranges)
            return klines[-limit:]
        except Exception as e:
            self.logger.error(
                f'Failed to request data | Bybit | {symbol} | '
                f'{interval.value} | {type(e).__name__} - {e}'
            )
            return []

    @lru_cache
    def get_price_precision(self, symbol: str) -> float:
        try:
            symbol_info = self._get_symbol_info(symbol)
            return float(symbol_info['priceFilter']['tickSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get price precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )

    @lru_cache
    def get_qty_precision(self, symbol: str) -> float:
        try:
            symbol_info = self._get_symbol_info(symbol)
            lot_size_filter = symbol_info['lotSizeFilter']
            return float(lot_size_filter['qtyStep'])
        except Exception as e:
            self.logger.error(
                f'Failed to get qty precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )

    def get_tickers(self, symbol: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/market/tickers'
        params = {'category': 'linear', 'symbol': symbol}
        return self.get(url, params)

    def get_valid_interval(self, interval: Interval) -> str:
        try:
            return self._INTERVAL_MAP[interval]
        except KeyError:
            raise ValueError(f'Invalid interval: {interval}')

    def get_interval_duration(self, interval: Interval) -> int:
        try:
            return self._INTERVAL_MS_MAP[interval]
        except KeyError:
            raise ValueError(f'Invalid interval: {interval}')

    def _fetch_concurrently(
        self,
        symbol: str,
        interval: Interval,
        time_ranges: list[tuple[int, int]]
    ) -> list:
        """
        Internal method to fetch data concurrently using ThreadPoolExecutor.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            time_ranges: List of (start, end) tuples in milliseconds
            
        Returns:
            list: Combined results from all concurrent requests
        """

        with ThreadPoolExecutor(max_workers=self._MAX_WORKERS) as executor:
            klines_grouped_by_range = executor.map(
                lambda time_range: self._get_klines(
                    symbol=symbol,
                    interval=interval,
                    start=time_range[0],
                    end=time_range[1]
                ),
                time_ranges
            )
            return [
                kline
                for kline_group in klines_grouped_by_range
                for kline in kline_group
            ]

    def _get_klines(
        self,
        symbol: str,
        interval: Interval,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        """
        Internal method to fetch kline data from Bybit API.
        
        Makes direct API call to retrieve kline data with specified params.
        Used internally by public kline methods.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            start: Start time in milliseconds
            end: End time in milliseconds
            limit: Maximum number of klines (default: 1000)
        
        Returns:
            list: Raw kline data from API
        """

        url = f'{self.BASE_ENDPOINT}/v5/market/kline'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': self.get_valid_interval(interval),
            'limit': limit,
        }

        if start:
            params['start'] = start

        if end:
            params['end'] = end

        response = self.get(url, params, logging=False)
        return response['result']['list'][::-1]

    def _get_symbol_info(self, symbol: str) -> dict:
        """
        Get symbol information from exchange info.
        
        Retrieves detailed symbol information including filters, precision,
        and trading rules from exchange info endpoint.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
        
        Returns:
            dict: Symbol information with filters and rules
        """

        url = f'{self.BASE_ENDPOINT}/v5/market/instruments-info'
        params = {'category': 'linear', 'symbol': symbol}
        response = self.get(url, params)
        return response['result']['list'][0]