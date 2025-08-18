from logging import getLogger
from time import sleep, time
from typing import TYPE_CHECKING

import numpy as np

from src.core.quantklines import shrink, stretch
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

    def get_market_data(
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
                - symbol: Trading symbol
                - interval: Validated interval
                - precision: Price and quantity precision
                - klines: Historical kline data
                - additional feeds (if configured)
        """

        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)   
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

        feeds_data = (
            self._get_feeds_data(
                client=client,
                main_interval=valid_interval,
                main_klines=klines,
                symbol=symbol,
                feeds=feeds,
            )
            if feeds
            else {'feeds': {}}
        )

        result = {
            'symbol': symbol,
            'interval': valid_interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            **feeds_data
        }

        return result

    def _get_feeds_data(
        self,
        client: 'BinanceClient | BybitClient',
        symbol: str,
        feeds: dict,
        main_interval: str | int,
        main_klines: np.ndarray
    ) -> dict:
        """
        Fetch additional data feeds based on configuration.
        
        Currently supports secondary klines feeds with different
        symbols or intervals, resampled to match the main kline array.

        Args:
            client: Exchange API client
            symbol: Base trading symbol
            feeds: Configuration dictionary specifying additional feeds
            main_interval: Interval of the main kline array
            main_klines: Main array of klines used as reference for resampling

        Returns:
            dict: Requested feeds data, structured as:
                {
                    'feeds': {
                        'klines': {feed_name: np.ndarray, ...},
                        'raw_klines': {feed_name: np.ndarray, ...}
                    }
                }
        """

        if 'klines' not in feeds:
            return {}
        
        klines_by_feed = {}
        raw_klines_by_feed = {}

        for feed_name, feed_config in feeds['klines'].items():
            feed_key, feed_interval_key = feed_config[:2]
            feed_symbol = symbol if feed_key == 'symbol' else feed_key
            feed_interval = client.get_valid_interval(feed_interval_key)

            main_ms = client.INTERVAL_MS[main_interval]
            feed_ms = client.INTERVAL_MS[feed_interval]

            current_ms = int(time() * 1000)
            main_start_ms = main_klines[0][0]
            limit = int((current_ms - main_start_ms) / feed_ms)

            raw_klines = client.get_last_klines(
                symbol=feed_symbol,
                interval=feed_interval,
                limit=limit
            )
            klines = np.array(raw_klines)[:, :6].astype(float)

            if has_realtime_kline(klines):
                klines = klines[:-1]

            raw_klines_by_feed[feed_name] = klines.copy()

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

        return {
            'feeds': {
                'klines': klines_by_feed,
                'raw_klines': raw_klines_by_feed
            }
        }

    def update_data(self, strategy_context: dict) -> bool:
        """
        Update market data for a strategy context.

        Args:
            strategy_context: Strategy context to update

        Returns:
            bool: True if data was updated, False otherwise
        """

        client = strategy_context['client']
        market_data = strategy_context['market_data']
        feeds = market_data.get('feeds', {})
        main_klines_updated = False

        if not has_last_historical_kline(market_data['klines']):
            market_data['klines'] = self._append_last_kline(
                klines=market_data['klines'],
                client=client,
                symbol=market_data['symbol'],
                interval=market_data['interval']
            )
            main_klines_updated = True

        if 'klines' in feeds:
            raw_klines = feeds['raw_klines']
            main_klines = market_data['klines']
            main_interval = market_data['interval']
            main_ms = client.INTERVAL_MS[main_interval]

            for feed_name in feeds['klines'].keys():
                feed_config = (
                    strategy_context['instance']
                    .params['feeds']['klines'][feed_name]
                )
                feed_klines_updated = False

                if not has_last_historical_kline(raw_klines[feed_name]):
                    feed_key, feed_interval_key = feed_config[:2]
                    feed_symbol = (
                        market_data['symbol'] 
                        if feed_key == 'symbol' 
                        else feed_key
                    )
                    feed_interval = (
                        client.get_valid_interval(feed_interval_key)
                    )

                    raw_klines[feed_name] = self._append_last_kline(
                        klines=raw_klines[feed_name],
                        client=client,
                        symbol=feed_symbol,
                        interval=feed_interval
                    )
                    feed_klines_updated = True

                if main_klines_updated or feed_klines_updated:
                    feed_interval = client.get_valid_interval(feed_config[1])
                    feed_ms = client.INTERVAL_MS[feed_interval]
                    
                    if main_ms <= feed_ms:
                        feeds['klines'][feed_name] = stretch(
                            higher_tf_data=raw_klines[feed_name],
                            higher_tf_time=raw_klines[feed_name][:, 0],
                            target_tf_time=main_klines[:, 0]
                        )
                    else:
                        feeds['klines'][feed_name] = shrink(
                            lower_tf_data=raw_klines[feed_name],
                            lower_tf_time=raw_klines[feed_name][:, 0],
                            target_tf_time=main_klines[:, 0]
                        )

        return main_klines_updated

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
                sleep(1.0)
                continue

            return np.vstack([klines, new_kline])

        self.logger.warning(
            f'Failed to append new kline for {symbol} | {interval}'
        )
        return klines