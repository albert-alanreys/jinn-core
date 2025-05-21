from logging import getLogger
from typing import Callable

from .connection import WebSocketConnection


class KlineStream:
    BASE_WS_URL = 'wss://fstream.binance.com/ws'

    def __init__(self, on_kline: Callable) -> None:
        self.on_kline = on_kline

        self.ws = WebSocketConnection(self.BASE_WS_URL)
        self.logger = getLogger(__name__)

    def get_topic(self, symbol: str, interval: str) -> str:
        return f'{symbol.lower()}@kline_{interval}'

    def start_stream(self, topics: list) -> None:
        payload = {'method': 'SUBSCRIBE', 'params': topics}
        self.ws.listen(self.on_message, payload)

    def on_message(self, message: dict) -> None:
        try:
            if 'e' in message:
                topic = self.get_topic(message['s'], message['k']['i'])
                kline_data = message['k']

                if kline_data['x']:
                    kline = [
                        kline_data['t'],
                        float(kline_data['o']),
                        float(kline_data['h']),
                        float(kline_data['l']),
                        float(kline_data['c']),
                        float(kline_data['v'])
                    ]
                    self.on_kline({'topic': topic, 'kline': kline})
        except (KeyError, IndexError, ValueError) as e:
            self.logger.warning(
                f'Unexpected message format: {e} | raw: {message}'
            )