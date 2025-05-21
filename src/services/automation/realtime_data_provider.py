from logging import getLogger
from threading import Thread
from typing import TYPE_CHECKING

import numpy as np

import src.core.enums as enums
from src.core.utils.singleton import singleton
from src.services.automation.api_clients.bybit import BybitWebSocket

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceClient
    from src.services.automation.api_clients.bybit import BybitREST


@singleton
class RealtimeDataProvider:
    def __init__(self) -> None:
        self.topics_and_strategies = {}

        self.bybit_ws = BybitWebSocket(self.handle_kline_message)

        self.logger = getLogger(__name__)

    def get_data(
        self,
        client: 'BinanceClient | BybitREST',
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
        for item in strategies.values():
            match item['client'].exchange:
                case enums.Exchange.BINANCE:
                    pass
                case enums.Exchange.BYBIT:
                    topic = self.bybit_ws.get_topic(
                        interval=item['interval'],
                        symbol=item['symbol']
                    )

                    if topic not in self.topics_and_strategies:
                        self.topics_and_strategies[topic] = [item]
                    else:
                        self.topics_and_strategies[topic].append(item)

        self.bybit_ws.start_stream(list(self.topics_and_strategies.keys()))

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