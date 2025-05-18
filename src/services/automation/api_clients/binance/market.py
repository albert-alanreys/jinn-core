import logging
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

from src.core.enums import Market
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

    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)
        self.logger = logging.getLogger(__name__)

    def get_historical_klines(
        self,
        market: Market,
        symbol: str,
        interval: str,
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
        try:
            if limit <= 1000:
                return self._get_klines(
                    market=Market.FUTURES,
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )

            interval_ms = self.interval_ms[interval]
            end = int(time.time() * 1000)
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
                f'Binance | '
                f'{Market.FUTURES.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{type(e).__name__} - {e}'

            )
            return []

    @lru_cache
    def get_price_precision(self, symbol: str) -> float:
        try:
            symbols_info = self._get_exchange_info()['symbols']
            symbol_info = next(
                filter(lambda x: x['symbol'] == symbol, symbols_info)
            )
            return float(symbol_info['filters'][0]['tickSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get price precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )
            return 0.0

    @lru_cache
    def get_qty_precision(self, symbol: str) -> float:
        try:
            symbols_info = self._get_exchange_info()['symbols']
            symbol_info = next(
                filter(lambda x: x['symbol'] == symbol, symbols_info)
            )
            return float(symbol_info['filters'][1]['stepSize'])
        except Exception as e:
            self.logger.error(
                f'Failed to get qty precision for {symbol} | '
                f'{type(e).__name__} - {e}'
            )
            return 0.0

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
        market: Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list:
        match market:
            case Market.FUTURES:
                url = f'{self.futures_endpoint}/fapi/v1/klines'
            case Market.SPOT:
                url = f'{self.spot_endpoint}/api/v3/klines'

        params = {'symbol': symbol, 'interval': interval, 'limit': limit}

        if start:
            params['startTime'] = start

        if end:
            params['endTime'] = end

        return self.get(url, params, logging=False)