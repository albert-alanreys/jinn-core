from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache

import src.core.enums as enums
from .base import BaseClient


class MarketClient(BaseClient):
    intervals = {
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
    interval_ms = {
        '1m': 60 * 1000,
        '5m': 5 * 60 * 1000,
        '15m': 15 * 60 * 1000,
        '30m': 30 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '2h': 2 * 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '6h': 6 * 60 * 60 * 1000,
        '12h': 12 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    }

    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def get_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: str,
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
        return self._get_klines(
            market=enums.Market.FUTURES,
            symbol=symbol,
            interval=interval,
            limit=limit
        )

    @lru_cache
    def get_price_precision(self, symbol: str) -> float:
        symbols_info = self._get_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info)
        )
        return float(symbol_info['filters'][0]['tickSize'])

    @lru_cache
    def get_qty_precision(self, symbol: str) -> float:
        symbols_info = self._get_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info)
        )
        return float(symbol_info['filters'][1]['stepSize'])

    def get_tickers(self, symbol: str) -> dict:
        url = f'{self.futures_endpoint}/fapi/v1/premiumIndex'
        params = {'symbol': symbol}
        return self.get(url, params)
    
    def get_valid_interval(self, interval: str | int) -> str:
        if interval in self.intervals:
            return self.intervals[interval]
        
        raise ValueError(f'Invalid interval: {interval}')

    def _get_exchange_info(self) -> dict:
        return self.get(f'{self.futures_endpoint}/fapi/v1/exchangeInfo')

    def _get_klines(
        self,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        match market:
            case enums.Market.FUTURES:
                url = f'{self.futures_endpoint}/fapi/v1/klines'
            case enums.Market.SPOT:
                url = f'{self.spot_endpoint}/api/v3/klines'

        params = {'symbol': symbol, 'interval': interval, 'limit': limit}

        if start:
            params['startTime'] = start

        if end:
            params['endTime'] = end

        return self.get(url, params, logging=False)