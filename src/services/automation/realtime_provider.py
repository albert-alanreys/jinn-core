from collections import defaultdict
from logging import getLogger
from threading import Thread
from time import time
from typing import TYPE_CHECKING

import numpy as np

import src.core.enums as enums
from src.core.utils.klines import has_realtime_kline
from src.services.automation.api_clients.binance import BinanceWebSocket
from src.services.automation.api_clients.bybit import BybitWebSocket

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceREST
    from src.services.automation.api_clients.bybit import BybitREST


class RealtimeProvider():
    KLINES_LIMIT = 3000

    def __init__(self) -> None:
        self.base_topic_to_states = defaultdict(list)
        self.extra_topic_to_states = defaultdict(list)

        self.binance_ws = BinanceWebSocket(self.handle_kline_message)
        self.bybit_ws = BybitWebSocket(self.handle_kline_message)

        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceREST | BybitREST',
        symbol: str,
        interval: str,
        extra_feeds: list | None
    ) -> dict:
        valid_interval = client.get_valid_interval(interval)
        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)

        klines = client.get_last_klines(
            symbol=symbol,
            interval=valid_interval,
            limit=self.KLINES_LIMIT
        )
        klines = np.array(klines)[:, :6].astype(float)

        if has_realtime_kline(klines):
            klines = klines[:-1]

        extra_klines_by_feed = {}

        if extra_feeds:
            for feed in extra_feeds:
                extra_symbol = symbol if feed[0] == 'symbol' else feed[0]
                extra_interval = client.get_valid_interval(feed[1])
                interval_ms = client.interval_ms[extra_interval]
                limit = int((time() * 1000 - klines[0][0]) / interval_ms)

                extra_klines = client.get_last_klines(
                    symbol=extra_symbol,
                    interval=extra_interval,
                    limit=limit
                )
                extra_klines = np.array(extra_klines)[:, :6].astype(float)

                if has_realtime_kline(extra_klines):
                    extra_klines = extra_klines[:-1]

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

    def subscribe_kline_updates(self, strategy_states: dict) -> None:
        binance_topics = set()
        bybit_topics = set()

        for strategy_state in strategy_states.values():
            client = strategy_state['client']
            market_data = strategy_state['market_data']
            symbol = market_data['symbol']
            base_interval = market_data['interval']
            extra_klines = market_data['extra_klines']

            match client.EXCHANGE:
                case enums.Exchange.BINANCE.value:
                    get_topic = self.binance_ws.get_topic
                    topics = binance_topics
                case enums.Exchange.BYBIT.value:
                    get_topic = self.bybit_ws.get_topic
                    topics = bybit_topics

            base_topic = get_topic(symbol=symbol, interval=base_interval)
            self.base_topic_to_states[base_topic].append(strategy_state)
            topics.add(base_topic)

            for (extra_symbol, extra_interval) in extra_klines:
                extra_topic = get_topic(
                    symbol=extra_symbol,
                    interval=extra_interval
                )
                self.extra_topic_to_states[extra_topic].append(
                    (strategy_state, (extra_symbol, extra_interval))
                )
                topics.add(extra_topic)

        if binance_topics:
            Thread(
                target=self.binance_ws.start_stream,
                args=(list(binance_topics),),
                daemon=True
            ).start()

        if bybit_topics:
            Thread(
                target=self.bybit_ws.start_stream,
                args=(list(bybit_topics),),
                daemon=True
            ).start()

    def handle_kline_message(self, message: dict) -> None:
        try:
            topic = message['topic']
            kline = message['kline']

            states_with_feeds = self.extra_topic_to_states.get(topic, [])
            strategy_states = self.base_topic_to_states.get(topic, [])

            for strategy_state, (symbol, interval) in states_with_feeds:
                market_data = strategy_state['market_data']
                key = (symbol, interval)

                market_data['extra_klines'][key] = np.vstack(
                    [market_data['extra_klines'][key], kline]
                )

            for strategy_state in strategy_states:
                market_data = strategy_state['market_data']
                market_data['klines'] = np.vstack(
                    [market_data['klines'], kline]
                )
                strategy_state['klines_updated'] = True
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')