from logging import getLogger
from time import sleep, time
from typing import TYPE_CHECKING

import numpy as np

import src.core.enums as enums
from src.core.utils.klines import has_last_historical_kline

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceClient
    from src.services.automation.api_clients.bybit import BybitClient


class RealtimeProvider():
    KLINES_LIMIT = 3000

    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str,
        extra_feeds: list | None
    ) -> dict:
        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)   

        valid_interval = client.get_valid_interval(interval)
        last_klines = client.get_last_klines(
            symbol=symbol,
            interval=valid_interval,
            limit=self.KLINES_LIMIT
        )
        klines = np.array(last_klines)[:, :6].astype(float)[:-1]

        extra_klines_by_feed = {}

        if extra_feeds:
            for feed in extra_feeds:
                extra_symbol = symbol if feed[0] == 'symbol' else feed[0]
                extra_interval = client.get_valid_interval(feed[1])
                interval_ms = client.interval_ms[extra_interval]
                limit = int((time() * 1000 - klines[0][0]) / interval_ms)

                last_klines = client.get_last_klines(
                    symbol=extra_symbol,
                    interval=extra_interval,
                    limit=limit
                )
                extra_klines = np.array(last_klines)[:, :6].astype(float)[:-1]

                key = (extra_symbol, extra_interval)
                extra_klines_by_feed[key] = extra_klines

        return {
            'market': enums.Market.FUTURES,
            'symbol': symbol,
            'interval': valid_interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            'extra_klines': extra_klines_by_feed
        }

    def update_data(self, strategy_state: dict) -> None:
        market_data = strategy_state['market_data']
        extra_klines = market_data['extra_klines']
        klines_updated = False

        if not has_last_historical_kline(market_data['klines']):
            market_data['klines'] = self._append_last_kline(
                klines=market_data['klines'],
                client=strategy_state['client'],
                symbol=market_data['symbol'],
                interval=market_data['interval']
            )
            klines_updated = True

        for feed, klines in extra_klines.items():
            if not has_last_historical_kline(klines):
                extra_klines[feed] = self._append_last_kline(
                    klines=klines,
                    client=strategy_state['client'],
                    symbol=feed[0],
                    interval=feed[1]
                )

        return klines_updated

    def _append_last_kline(
        self,
        klines: np.ndarray,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str
    ) -> np.ndarray:
        max_retries = 5

        for _ in range(max_retries):
            last_klines = client.get_last_klines(
                symbol=symbol,
                interval=interval,
                limit=2
            )

            if len(last_klines) != 2:
                continue

            new_kline = np.array(last_klines)[:, :6].astype(float)[:-1]

            if new_kline[0][0] <= klines[-1][0]:
                sleep(3.0)
                continue

            return np.vstack([klines, new_kline])

        self.logger.warning(
            f'Failed to append new kline for {symbol} | {interval}'
        )
        return klines