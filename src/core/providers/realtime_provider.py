from __future__ import annotations
from time import sleep, time
from typing import TYPE_CHECKING

import numpy as np

from src.core.quantklines import shrink, stretch
from src.infrastructure.exchanges.models import Interval
from src.shared.utils import (
    has_last_historical_kline,
    has_realtime_kline
)

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient
    from .models import MarketData, FeedsData


class RealtimeProvider():
    """Provides real-time market data for automated trading."""

    _KLINES_LIMIT = 1000

    def get_market_data(
        self,
        client: BaseExchangeClient,
        symbol: str,
        interval: Interval,
        feeds: dict | None
    ) -> MarketData:
        """
        Fetch initial real-time market data for a symbol.

        Args:
            client: Exchange API client for data fetching
            symbol: Trading symbol to fetch data for
            interval: Time interval for klines
            feeds: Additional data feeds configuration

        Returns:
            MarketData: Market data package matching MarketData structure
        """

        p_precision = client.market.get_price_precision(symbol)
        q_precision = client.market.get_qty_precision(symbol)   

        klines = np.array(
            client.market.get_last_klines(
                symbol=symbol,
                interval=interval,
                limit=self._KLINES_LIMIT
            )
        )[:, :6].astype(float)

        if has_realtime_kline(klines):
            klines = klines[:-1]

        feeds_data = (
            self._get_feeds_data(
                client=client,
                main_interval=interval,
                main_klines=klines,
                symbol=symbol,
                feeds=feeds,
            )
            if feeds else {}
        )

        return {
            'symbol': symbol,
            'interval': interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            'feeds': feeds_data,
        }

    def _get_feeds_data(
        self,
        client: BaseExchangeClient,
        symbol: str,
        feeds: dict,
        main_interval: Interval,
        main_klines: np.ndarray
    ) -> FeedsData:
        """
        Fetch additional data feeds based on configuration.
        
        Currently supports secondary klines feeds with different
        symbols or intervals, resampled to match the main kline array.

        Args:
            client: Exchange API client for data fetching
            symbol: Base trading symbol
            feeds: Configuration dictionary specifying additional feeds
            main_interval: Interval of the main kline array
            main_klines: Main array of klines

        Returns:
            FeedsData: Feeds data package matching FeedsData structure
        """

        if 'klines' not in feeds:
            return {}
        
        klines_by_feed: dict[str, np.ndarray] = {}
        raw_klines_by_feed: dict[str, np.ndarray] = {}

        for feed_name, feed_config in feeds['klines'].items():
            feed_key, feed_interval = feed_config[:2]
            feed_symbol = symbol if feed_key == 'symbol' else feed_key

            main_ms = client.market.get_interval_duration(main_interval)
            feed_ms = client.market.get_interval_duration(feed_interval)

            current_ms = int(time() * 1000)
            main_start_ms = main_klines[0][0]
            limit = int((current_ms - main_start_ms) / feed_ms)

            raw_klines = client.market.get_last_klines(
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
            'klines': klines_by_feed,
            'raw_klines': raw_klines_by_feed
        }

    def update_data(self, strategy_context: dict) -> bool:
        """
        Update market data for a strategy context.

        Args:
            strategy_context: Strategy context dictionary

        Returns:
            bool: True if main klines was updated, False otherwise
        """

        client = strategy_context['client']
        original_market_data = strategy_context['market_data']

        new_market_data = {
            'klines': original_market_data['klines'].copy(),
            'feeds': {'klines': {}, 'raw_klines': {}}
            if 'feeds' in original_market_data else None
        }

        main_klines_updated = False

        if not has_last_historical_kline(original_market_data['klines']):
            new_market_data['klines'] = self._append_last_kline(
                client=client,
                symbol=original_market_data['symbol'],
                interval=original_market_data['interval'],
                klines=original_market_data['klines']

            )
            main_klines_updated = True

        if new_market_data['feeds'] is not None:
            self._update_feeds(
                strategy_context=strategy_context,
                client=client,
                original_market_data=original_market_data,
                new_market_data=new_market_data,
                main_klines_updated=main_klines_updated
            )

        if main_klines_updated:
            strategy_context['market_data'].update(new_market_data)

        return main_klines_updated

    def _update_feeds(
        self,
        strategy_context: dict,
        client: BaseExchangeClient,
        original_market_data: dict,
        new_market_data: dict,
        main_klines_updated: bool,
    ) -> None:
        """
        Update feed klines and align them with main klines if needed.

        Args:
            strategy_context: Strategy context dictionary
            client: Exchange API client for data fetching
            original_market_data: Original market data before update
            new_market_data: Target dict for updated market data
            main_klines_updated: Whether the main klines were updated

        Returns:
            None
        """

        main_ms = client.market.get_interval_duration(
            original_market_data['interval']
        )

        for feed_name, feed_data in (
            original_market_data['feeds'].get('raw_klines', {}).items()
        ):
            new_market_data['feeds']['raw_klines'][feed_name] = (
                feed_data.copy()
            )

            has_last_kline = has_last_historical_kline(feed_data)
            need_feed_params = (not has_last_kline or main_klines_updated)

            if need_feed_params:
                feed_config = (
                    strategy_context['instance']
                    .params['feeds']['klines'][feed_name]
                )
                feed_key, feed_interval = feed_config[:2]
                feed_symbol = (
                    original_market_data['symbol']
                    if feed_key == 'symbol'
                    else feed_key
                )
                feed_ms = client.market.get_interval_duration(feed_interval)

            if not has_last_kline:
                new_market_data['feeds']['raw_klines'][feed_name] = (
                    self._append_last_kline(
                        client=client,
                        symbol=feed_symbol,
                        interval=feed_interval,
                        klines=feed_data
                    )
                )

            if main_klines_updated:
                self._resample_feed(
                    main_ms=main_ms,
                    feed_ms=feed_ms,
                    feed_name=feed_name,
                    new_market_data=new_market_data
                )

    def _resample_feed(
        self,
        main_ms: int,
        feed_ms: int,
        feed_name: str,
        new_market_data: dict
    ) -> None:
        """
        Resample feed data to match the main klines timeframe.

        Depending on whether the feed interval is higher or lower than
        the main interval, the data is either stretched or shrunk.

        Args:
            main_ms: Milliseconds duration of the main klines interval
            feed_ms: Milliseconds duration of the feed klines interval
            feed_name: Feed identifier
            new_market_data: Container for updated feed data

        Returns:
            None
        """

        feed_data = new_market_data['feeds']['raw_klines'][feed_name]
        feed_time = feed_data[:, 0]

        if main_ms <= feed_ms:
            new_market_data['feeds']['klines'][feed_name] = stretch(
                higher_tf_data=feed_data,
                higher_tf_time=feed_time,
                target_tf_time=new_market_data['klines'][:, 0],
            )
        else:
            new_market_data['feeds']['klines'][feed_name] = shrink(
                lower_tf_data=feed_data,
                lower_tf_time=feed_time,
                target_tf_time=new_market_data['klines'][:, 0],
            )

    def _append_last_kline(
        self,
        client: BaseExchangeClient,
        symbol: str,
        interval: Interval,
        klines: np.ndarray
    ) -> np.ndarray:
        """
        Append the latest kline to existing kline data.

        Args:
            client: Exchange API client for data fetching
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Kline interval from Interval enum
            klines: Existing kline array


        Returns:
            np.ndarray: Updated kline array with new data
        """

        max_retries = 5

        for _ in range(max_retries):
            last_klines = client.market.get_last_klines(
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

        return klines