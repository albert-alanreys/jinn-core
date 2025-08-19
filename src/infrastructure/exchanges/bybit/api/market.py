from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from logging import getLogger
from time import time

from .base import BaseBybitClient


class MarketClient(BaseBybitClient):
    """
    Client for Bybit market data operations.
    
    Handles market data retrieval including klines, tickers,
    symbol information, and precision data.
    """

    _INTERVALS = {
        1: 1, '1': 1, '1m': 1,
        5: 5, '5': 5, '5m': 5,
        15: 15, '15': 15, '15m': 15,
        30: 30, '30': 30, '30m': 30,
        60: 60, '60': 60, '1h': 60,
        120: 120, '120': 120, '2h': 120,
        240: 240, '240': 240, '4h': 240,
        360: 360, '360': 360, '6h': 360,
        720: 720, '720': 720, '12h': 720,
        'D': 'D', 'd': 'D', '1d': 'D',
    }
    _INTERVAL_MS = {
        1: 60000,
        5: 300000,
        15: 900000,
        30: 1800000,
        60: 3600000,
        120: 7200000,
        240: 14400000,
        360: 21600000,
        720: 43200000,
        'D': 86400000,
    }
    _MAX_WORKERS = 50

    def __init__(self) -> None:
        """Initialize market client with base client functionality."""

        super().__init__()
        self.logger = getLogger(__name__)

    def get_historical_klines(
        self,
        symbol: str,
        interval: str | int,
        start: int,
        end: int
    ) -> list:
        try:
            interval = self.get_valid_interval(interval)
            interval_ms = self._INTERVAL_MS[interval]
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            return self._fetch_concurrently(symbol, interval, time_ranges)
        except Exception as e:
            self.logger.error(
                f'Failed to request data | Bybit | {symbol} | '
                f'{interval} | {type(e).__name__} - {e}'
            )
            return []

    def get_last_klines(
        self,
        symbol: str,
        interval: str | int,
        limit: int = 1000
    ) -> list:
        try:
            interval = self.get_valid_interval(interval)

            if limit <= 1000:
                return self._get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )

            interval_ms = self._INTERVAL_MS[interval]
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
                f'{interval} | {type(e).__name__} - {e}'
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

    @lru_cache
    def get_valid_interval(self, interval: str | int) -> str:
        if interval in self._INTERVALS:
            return self._INTERVALS[interval]
        
        raise ValueError(f'Invalid interval: {interval}')
    
    @lru_cache
    def get_interval_duration(self, interval: str | int) -> int:
        return self._INTERVAL_MS[self.get_valid_interval(interval)]

    def _fetch_concurrently(
        self,
        symbol: str,
        interval: str | int,
        time_ranges: list[tuple[int, int]]
    ) -> list:
        """
        Internal method to fetch data concurrently using ThreadPoolExecutor.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            interval (str | int): Kline interval (e.g., '1m', 60)
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
        interval: str | int,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        """
        Internal method to fetch kline data from Bybit API.
        
        Makes direct API call to retrieve kline data with specified params.
        Used internally by public kline methods.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            interval (str | int): Kline interval (e.g., '1m', 60)
            start (int, optional): Start time in milliseconds
            end (int, optional): End time in milliseconds
            limit (int): Maximum number of klines (default: 1000)
        
        Returns:
            list: Raw kline data from API
        """

        url = f'{self.BASE_ENDPOINT}/v5/market/kline'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': interval,
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
            symbol (str): Trading symbol (e.g., BTCUSDT)
        
        Returns:
            dict: Symbol information with filters and rules
        """

        url = f'{self.BASE_ENDPOINT}/v5/market/instruments-info'
        params = {'category': 'linear', 'symbol': symbol}
        response = self.get(url, params)

        return response['result']['list'][0]