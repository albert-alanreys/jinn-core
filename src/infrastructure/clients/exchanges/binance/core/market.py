from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from logging import getLogger
from time import time

from src.core.enums import Market
from .base import BaseClient


class MarketClient(BaseClient):
    """
    Client for Binance market data operations.
    
    Handles market data retrieval including klines, tickers,
    symbol information, and precision data.
    Supports both futures and spot markets.
    
    Attributes:
        INTERVALS (dict): Mapping of interval formats to standard intervals
        INTERVAL_MS (dict): Interval durations in milliseconds

    Instance Attributes:
        logger: Logger instance for this module
    """

    INTERVALS = {
        '1m': '1m', '1': '1m', 1: '1m',
        '5m': '5m', '5': '5m', 5: '5m',
        '15m': '15m', '15': '15m', 15: '15m',
        '30m': '30m', '30': '30m', 30: '30m',
        '1h': '1h', '60': '1h', 60: '1h',
        '2h': '2h', '120': '2h', 120: '2h',
        '4h': '4h', '240': '4h', 240: '4h',
        '6h': '6h', '360': '6h', 360: '6h',
        '12h': '12h', '720': '12h', 720: '12h',
        '1d': '1d', 'd': '1d', 'D': '1d',
    }
    INTERVAL_MS = {
        '1m': 60000,
        '5m': 300000,
        '15m': 900000,
        '30m': 1800000,
        '1h': 3600000,
        '2h': 7200000,
        '4h': 14400000,
        '6h': 21600000,
        '12h': 43200000,
        '1d': 86400000,
    }

    def __init__(self) -> None:
        """Initialize market client with base client functionality."""

        super().__init__()

        self.logger = getLogger(__name__)

    def get_historical_klines(
        self,
        market: Market,
        symbol: str,
        interval: str,
        start: int,
        end: int
    ) -> list:
        """
        Retrieve historical kline data for specified time range.
        
        Fetches kline data by breaking large time ranges into smaller chunks
        and processing them concurrently for improved performance.
        
        Args:
            market (Market): Market type (FUTURES or SPOT)
            symbol (str): Trading symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1m', '1h', '1d')
            start (int): Start time in milliseconds
            end (int): End time in milliseconds
            
        Returns:
            list: Historical kline data with OHLCV information
        """

        try:
            interval = self.get_valid_interval(interval)
            interval_ms = self.INTERVAL_MS[interval]
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            klines = []

            with ThreadPoolExecutor(max_workers=20) as executor:
                klines_grouped_by_range = executor.map(
                    lambda time_range: self._get_klines(
                        market=market,
                        symbol=symbol,
                        interval=interval,
                        start=time_range[0],
                        end=time_range[1]
                    ),
                    time_ranges
                )
                klines = [
                    kline
                    for kline_group in klines_grouped_by_range
                    for kline in kline_group
                ]

            return klines
        except Exception as e:
            self.logger.error(
                f'Failed to request data | '
                f'Binance | '
                f'{market.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{type(e).__name__} - {e}'
            )
            return []

    def get_last_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000
    ) -> list:
        """
        Retrieve recent kline data for specified symbol.
        
        Fetches the most recent kline data up to the specified limit.
        For limits > 1000, uses time range chunking with concurrent requests.
        
        Args:
            symbol (str): Trading symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1m', '1h', '1d')
            limit (int): Number of klines to retrieve (default: 1000)
            
        Returns:
            list: Recent kline data with OHLCV information
        """

        try:
            interval = self.get_valid_interval(interval)

            if limit <= 1000:
                return self._get_klines(
                    market=Market.FUTURES,
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )

            interval_ms = self.INTERVAL_MS[interval]
            end = int(time() * 1000)
            end = end - (end % interval_ms)
            start = end - interval_ms * limit
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            klines = []

            with ThreadPoolExecutor(max_workers=20) as executor:
                klines_grouped_by_range = executor.map(
                    lambda time_range: self._get_klines(
                        market=Market.FUTURES,
                        symbol=symbol,
                        interval=interval,
                        start=time_range[0],
                        end=time_range[1]
                    ),
                    time_ranges
                )
                klines = [
                    kline
                    for kline_group in klines_grouped_by_range
                    for kline in kline_group
                ]

            return klines[-limit:]
        except Exception as e:
            self.logger.error(
                f'Failed to request data | '
                f'Binance | '
                f'{Market.FUTURES.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{type(e).__name__} - {e}'
            )
            return []

    @lru_cache
    def get_valid_interval(self, interval: str | int) -> str:
        """
        Convert interval input to valid Binance interval format.
        
        Validates and normalizes interval input, supporting various formats
        including strings and integers.
        
        Args:
            interval (str | int): Interval in various formats
            
        Returns:
            str: Standardized interval string
            
        Raises:
            ValueError: If interval format is invalid
        """

        if interval in self.INTERVALS:
            return self.INTERVALS[interval]
        
        raise ValueError(f'Invalid interval: {interval}')

    @lru_cache
    def get_price_precision(self, market: Market, symbol: str) -> float:
        """
        Get price precision (tick size) for specified symbol.
        
        Retrieves the minimum price increment for the symbol
        from exchange info. Result is cached for performance.
        
        Args:
            market (Market): Market type (FUTURES or SPOT)
            symbol (str): Trading symbol
            
        Returns:
            float: Price precision value (tick size)
        """

        try:
            symbol_info = self._get_symbol_info(market, symbol)
            return float(symbol_info['filters'][0]['tickSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get price precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )

    @lru_cache
    def get_qty_precision(self, market: Market, symbol: str) -> float:
        """
        Get quantity precision (step size) for specified symbol.
        
        Retrieves the minimum quantity increment for the symbol
        from exchange info. Result is cached for performance.
        
        Args:
            market (Market): Market type (FUTURES or SPOT)
            symbol (str): Trading symbol
            
        Returns:
            float: Quantity precision value (step size)
        """

        try:
            symbol_info = self._get_symbol_info(market, symbol)
            return float(symbol_info['filters'][1]['stepSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get qty precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )

    def get_tickers(self, symbol: str) -> dict:
        """
        Get ticker information including mark price for futures symbol.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            dict: Ticker information with prices and rates
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/premiumIndex'
        params = {'symbol': symbol}
        return self.get(url, params)

    def _get_klines(
        self,
        market: Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        """
        Internal method to fetch kline data from Binance API.
        
        Makes direct API call to retrieve kline data with specified params.
        Used internally by public kline methods.
        
        Args:
            market (Market): Market type (FUTURES or SPOT)
            symbol (str): Trading symbol
            interval (str): Kline interval
            start (int, optional): Start time in milliseconds
            end (int, optional): End time in milliseconds
            limit (int): Maximum number of klines (default: 1000)
            
        Returns:
            list: Raw kline data from API
        """

        match market:
            case Market.FUTURES:
                url = f'{self.FUTURES_ENDPOINT}/fapi/v1/klines'
            case Market.SPOT:
                url = f'{self.SPOT_ENDPOINT}/api/v3/klines'

        params = {'symbol': symbol, 'interval': interval, 'limit': limit}

        if start:
            params['startTime'] = start

        if end:
            params['endTime'] = end

        return self.get(url, params, logging=False)

    def _get_symbol_info(self, market: Market, symbol: str) -> dict:
        """
        Get symbol information from exchange info.
        
        Retrieves detailed symbol information including filters, precision,
        and trading rules from exchange info endpoint.
        
        Args:
            market (Market): Market type (FUTURES or SPOT)
            symbol (str): Trading symbol
            
        Returns:
            dict: Symbol information with filters and rules
        """

        match market:
            case Market.FUTURES:
                url = f'{self.FUTURES_ENDPOINT}/fapi/v1/exchangeInfo'
            case Market.SPOT:
                url = f'{self.SPOT_ENDPOINT}/api/v3/exchangeInfo'

        symbols_info = self.get(url)['symbols']
        return next(
            filter(lambda x: x['symbol'] == symbol, symbols_info)
        )