from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache

import src.core.enums as enums
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
        1: 60 * 1000,
        5: 5 * 60 * 1000,
        15: 15 * 60 * 1000,
        30: 30 * 60 * 1000,
        60: 60 * 60 * 1000,
        120: 2 * 60 * 60 * 1000,
        240: 4 * 60 * 60 * 1000,
        360: 6 * 60 * 60 * 1000,
        720: 12 * 60 * 60 * 1000,
        'D': 24 * 60 * 60 * 1000,
    }

    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def get_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: str | int,
        start: str,
        end: str
    ) -> list:
        start = int(
            datetime.strptime(start, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        end = int(
            datetime.strptime(end, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
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

    def get_last_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000
    ) -> list:
        klines = self._get_klines(
            market=enums.Market.FUTURES,
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        if klines is None:
            return []

        return klines

    @lru_cache
    def get_price_precision(self, symbol: str) -> float:
        symbol_info = (
            self._get_symbol_info(symbol)['result']['list'][0]
        )
        return float(symbol_info['priceFilter']['tickSize'])

    @lru_cache
    def get_qty_precision(self, symbol: str) -> float:
        symbol_info = (
            self._get_symbol_info(symbol)['result']['list'][0]
        )
        return float(symbol_info['lotSizeFilter']['qtyStep'])

    def get_tickers(self, symbol: str) -> dict:
        url = f'{self.base_endpoint}/v5/market/tickers'
        params = {'category': 'linear', 'symbol': symbol}
        return self.get(url, params)

    def get_valid_interval(self, interval: str | int) -> str | int:
        if interval in self.intervals:
            return self.intervals[interval]
        
        raise ValueError(f'Invalid interval: {interval}')

    def _get_klines(
        self,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> dict | None:
        url = f'{self.base_endpoint}/v5/market/kline'
        
        match market:
            case enums.Market.FUTURES:
                category = 'linear'
            case enums.Market.SPOT:
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
        url = f'{self.base_endpoint}/v5/market/instruments-info'
        params = {'category': 'linear', 'symbol': symbol}
        return self.get(url, params)