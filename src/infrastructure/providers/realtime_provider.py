from logging import getLogger
from time import sleep, time
from typing import TYPE_CHECKING

import numpy as np

from src.core.enums import Market
from src.utils.klines import has_last_historical_kline
from src.utils.klines import has_realtime_kline

if TYPE_CHECKING:
    from src.infrastructure.clients.exchanges.binance import BinanceClient
    from src.infrastructure.clients.exchanges.bybit import BybitClient


class RealtimeProvider():
    """
    Provides real-time market data for automated trading.

    Handles fetching and updating of real-time market data including
    klines and additional feed data required by strategies.
    Manages data precision and validity checks.

    Attributes:
        KLINES_LIMIT (int): Maximum number of klines to fetch (default: 3000)
    """

    KLINES_LIMIT = 3000

    def __init__(self) -> None:
        """
        Initialize RealtimeProvider.

        Sets up logger instance for data operations.
        """

        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
        feeds: dict | None
    ) -> dict:
        """
        Fetch initial real-time market data for a symbol.

        Args:
            client: Exchange API client instance
            symbol: Trading symbol to fetch data for
            interval: Time interval for klines
            feeds: Additional data feeds configuration

        Returns:
            dict: Complete market data dictionary including:
                - market: Market type
                - symbol: Trading symbol
                - interval: Validated interval
                - precision: Price and quantity precision
                - klines: Historical kline data
                - additional feeds (if configured)
        """

        p_precision = client.get_price_precision(Market.FUTURES, symbol)
        q_precision = client.get_qty_precision(Market.FUTURES, symbol)   

        valid_interval = client.get_valid_interval(interval)
        klines = np.array(
            client.get_last_klines(
                symbol=symbol,
                interval=valid_interval,
                limit=self.KLINES_LIMIT
            )
        )[:, :6].astype(float)

        if has_realtime_kline(klines):
            klines = klines[:-1]

        additional_data = self._fetch_additional_data(
            client=client,
            symbol=symbol,
            main_klines=klines,
            feeds=feeds
        ) if feeds else {'feeds': {}}

        result = {
            'market': Market.FUTURES,
            'symbol': symbol,
            'interval': valid_interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            **additional_data
        }

        return result

    def update_data(self, strategy_context: dict) -> bool:
        """
        Update market data for a strategy context.

        Args:
            strategy_context: Strategy context to update

        Returns:
            bool: True if data was updated, False otherwise
        """

        market_data = strategy_context['market_data']
        feeds = market_data.get('feeds', {})
        updated = False

        if not has_last_historical_kline(market_data['klines']):
            market_data['klines'] = self._append_last_kline(
                klines=market_data['klines'],
                client=strategy_context['client'],
                symbol=market_data['symbol'],
                interval=market_data['interval']
            )
            updated = True

        if 'klines' in feeds:
            for feed_name, klines in feeds['klines'].items():
                if not has_last_historical_kline(klines):
                    params = strategy_context['instance'].params
                    feed_config = params['feeds']['klines'][feed_name]
                    feed_symbol = (
                        market_data['symbol'] 
                        if feed_config[0] == 'symbol' 
                        else feed_config[0]
                    )
                    feed_interval = feed_config[1]

                    feeds['klines'][feed_name] = self._append_last_kline(
                        klines=klines,
                        client=strategy_context['client'],
                        symbol=feed_symbol,
                        interval=feed_interval
                    )

        return updated

    def _fetch_additional_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        main_klines: np.ndarray,
        feeds: dict
    ) -> dict:
        """
        Fetch additional feed data required by strategies.

        Args:
            client: Exchange API client
            symbol: Main trading symbol
            main_klines: Primary kline data
            feeds: Feed configuration dictionary

        Returns:
            dict: Dictionary containing all additional feed data
        """

        result = {}
        
        if 'klines' in feeds:
            klines_data = {}

            for feed_name, feed_config in feeds['klines'].items():
                feed_symbol = (
                    symbol if feed_config[0] == 'symbol' else feed_config[0]
                )
                feed_interval = client.get_valid_interval(feed_config[1])
                interval_ms = client.INTERVAL_MS[feed_interval]
                limit = int((time() * 1000 - main_klines[0][0]) / interval_ms)

                feed_klines = np.array(
                    client.get_last_klines(
                        symbol=feed_symbol,
                        interval=feed_interval,
                        limit=limit
                    )
                )[:, :6].astype(float)

                if has_realtime_kline(feed_klines):
                    feed_klines = feed_klines[:-1]

                klines_data[feed_name] = feed_klines

            if klines_data:
                result['feeds'] = {'klines': klines_data}

        return result

    def _append_last_kline(
        self,
        klines: np.ndarray,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        interval: str | int,
    ) -> np.ndarray:
        """
        Append the latest kline to existing kline data.

        Args:
            klines: Existing kline array
            client: Exchange API client
            symbol: Trading symbol
            interval: Kline interval

        Returns:
            np.ndarray: Updated kline array with new data
        """

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