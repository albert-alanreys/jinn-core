from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from logging import getLogger
from time import time

from src.core.enums import Market
from .base import BaseClient


class MarketClient(BaseClient):
    intervals = {
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
    interval_ms = {
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

    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)
        self.logger = getLogger(__name__)

    def get_historical_klines(
        self,
        market: Market,
        symbol: str,
        interval: str | int,
        start: int,
        end: int
    ) -> list:
        try:
            interval_ms = self.interval_ms[interval]
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            klines = []

            with ThreadPoolExecutor(max_workers=7) as executor:
                results = executor.map(
                    lambda time_range: self._get_klines(
                        market=market,
                        symbol=symbol,
                        interval=interval,
                        start=time_range[0],
                        end=time_range[1]
                    ),
                    time_ranges
                )

                for result in results:
                    klines.extend(result)

            return klines
        except Exception as e:
            self.logger.error(
                f'Failed to request data | '
                f'Bybit | '
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
        try:
            if limit <= 1000:
                return self._get_klines(
                    market=Market.FUTURES,
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )[:-1]

            interval_ms = self.interval_ms[interval]
            end = int(time() * 1000)
            start = end - interval_ms * limit
            step = interval_ms * 1000

            time_ranges = [
                (start, min(start + step - interval_ms, end))
                for start in range(start, end, step)
            ]
            klines = []

            with ThreadPoolExecutor(max_workers=7) as executor:
                results = executor.map(
                    lambda time_range: self._get_klines(
                        market=Market.FUTURES,
                        symbol=symbol,
                        interval=interval,
                        start=time_range[0],
                        end=time_range[1]
                    ),
                    time_ranges
                )

                for result in results:
                    klines.extend(result)

            return klines[-limit:]
        except Exception as e:
            self.logger.error(
                f'Failed to request data | '
                f'Bybit | '
                f'{Market.FUTURES.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{type(e).__name__} - {e}'
            )
            return []

    @lru_cache
    def get_price_precision(self, symbol: str) -> float:
        try:
            symbol_info = (
                self._get_symbol_info(symbol)['result']['list'][0]
            )
            return float(symbol_info['priceFilter']['tickSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get price precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )
            return 0.0

    @lru_cache
    def get_qty_precision(self, symbol: str) -> float:
        try:
            symbol_info = (
                self._get_symbol_info(symbol)['result']['list'][0]
            )
            return float(symbol_info['lotSizeFilter']['qtyStep'])
        except Exception as e:
            self.logger.error(
                f'Failed to get qty precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )
            return 0.0

    def get_tickers(self, symbol: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/market/tickers'
        params = {'category': 'linear', 'symbol': symbol}
        return self.get(url, params)

    def get_valid_interval(self, interval: str | int) -> str | int:
        if interval in self.intervals:
            return self.intervals[interval]
        
        raise ValueError(f'Invalid interval: {interval}')

    def _get_klines(
        self,
        market: Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        url = f'{self.BASE_ENDPOINT}/v5/market/kline'
        
        match market:
            case Market.FUTURES:
                category = 'linear'
            case Market.SPOT:
                category = 'spot'

        params = {
            'category': category,
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
        url = f'{self.BASE_ENDPOINT}/v5/market/instruments-info'
        params = {'category': 'linear', 'symbol': symbol}
        return self.get(url, params)