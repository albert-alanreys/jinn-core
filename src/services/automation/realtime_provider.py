from logging import getLogger
from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

import src.core.enums as enums
from src.services.automation.api_clients.binance import BinanceWebSocket
from src.services.automation.api_clients.bybit import BybitWebSocket

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceREST
    from src.services.automation.api_clients.bybit import BybitREST


class RealtimeProvider():
    def __init__(self) -> None:
        self.topic_to_states = {}

        self.binance_ws = BinanceWebSocket(self.handle_kline_message)
        self.bybit_ws = BybitWebSocket(self.handle_kline_message)

        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceREST | BybitREST',
        symbol: str,
        interval: str
    ) -> dict:
        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)

        klines = client.get_last_klines(
            symbol=symbol,
            interval=interval,
            limit=3000
        )
        klines = np.array(klines)[:, :6].astype(float)

        return {
            'market': enums.Market.FUTURES,
            'symbol': symbol,
            'interval': interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines
        }

    def subscribe_kline_updates(self, strategy_states: dict) -> None:
        binance_topics = []
        bybit_topics = []

        for strategy_state in strategy_states.values():
            match strategy_state['client'].EXCHANGE:
                case enums.Exchange.BINANCE.value:
                    topic = self.binance_ws.get_topic(
                        symbol=strategy_state['market_data']['symbol'],
                        interval=strategy_state['market_data']['interval']
                    )
                    binance_topics.append(topic)
                case enums.Exchange.BYBIT.value:
                    topic = self.bybit_ws.get_topic(
                        symbol=strategy_state['market_data']['symbol'],
                        interval=strategy_state['market_data']['interval']
                    )
                    bybit_topics.append(topic)

            if topic not in self.topic_to_states:
                self.topic_to_states[topic] = [strategy_state]
            else:
                self.topic_to_states[topic].append(strategy_state)

        if binance_topics:
            Thread(
                target=self.binance_ws.start_stream,
                args=(binance_topics,),
                daemon=True
            ).start()

        if bybit_topics:
            Thread(
                target=self.bybit_ws.start_stream,
                args=(bybit_topics,),
                daemon=True
            ).start()

    def handle_kline_message(self, message: dict) -> None:
        try:
            topic = message['topic']
            kline = message['kline']

            for strategy_state in self.topic_to_states[topic]:
                strategy_state['market_data']['klines'] = np.vstack(
                    [strategy_state['market_data']['klines'], kline]
                )
                strategy_state['klines_updated'] = True
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')