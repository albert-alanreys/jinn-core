from logging import getLogger
from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

import src.core.enums as enums
from src.core.utils.singleton import singleton
from src.services.automation.api_clients.binance import BinanceWebSocket
from src.services.automation.api_clients.bybit import BybitWebSocket

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceREST
    from src.services.automation.api_clients.bybit import BybitREST


@singleton
class RealtimeDataProvider:
    def __init__(self) -> None:
        self.topics_and_strategies = {}

        self.binance_ws = BinanceWebSocket(self.handle_kline_message)
        self.bybit_ws = BybitWebSocket(self.handle_kline_message)

        self.logger = getLogger(__name__)

    def get_data(
        self,
        client: 'BinanceREST | BybitREST',
        symbol: str,
        interval: str
    ) -> dict:
        data = client.get_last_klines(
            symbol=symbol,
            interval=interval,
            limit=3000
        )
        klines = np.array(data)[:, :6].astype(float)
        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)

        return {
            'market': enums.Market.FUTURES,
            'symbol': symbol,
            'klines': klines,
            'p_precision': p_precision,
            'q_precision': q_precision
        }

    def subscribe_kline_updates(self, strategies: dict) -> None:
        binance_topics = []
        bybit_topics = []

        for item in strategies.values():
            match item['client'].exchange:
                case enums.Exchange.BINANCE:
                    topic = self.binance_ws.get_topic(
                        symbol=item['symbol'],
                        interval=item['interval']
                    )
                    binance_topics.append(topic)
                case enums.Exchange.BYBIT:
                    topic = self.bybit_ws.get_topic(
                        symbol=item['symbol'],
                        interval=item['interval']
                    )
                    bybit_topics.append(topic)

            if topic not in self.topics_and_strategies:
                self.topics_and_strategies[topic] = [item]
            else:
                self.topics_and_strategies[topic].append(item)

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

            for strategy in self.topics_and_strategies[topic]:
                strategy['klines'] = np.vstack(
                    [strategy['klines'], kline]
                )
                strategy['klines_updated'] = True
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')