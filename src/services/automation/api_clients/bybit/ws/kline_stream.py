from logging import getLogger
from typing import Callable

from .connection import WebSocketConnection


class KlineStream:
    BASE_ENDPOINT = 'wss://stream.bybit.com/v5/public/linear'

    def __init__(self, on_kline: Callable) -> None:
        self.on_kline = on_kline

        self.ws = WebSocketConnection(self.BASE_ENDPOINT)
        self.logger = getLogger(__name__)

    def get_topic(self, interval: str, symbol: str) -> str:
        return f'kline.{interval}.{symbol}'

    def start_stream(self, topics: list) -> None:
        payload = {
            'req_id': 'subscribe',
            'op': 'subscribe',
            'args': topics
        }
        self.ws.listen(self._on_message, payload)

    def _on_message(self, message: dict) -> None:
        try:
            if 'data' in message:
                kline_data = message['data'][0]

                if kline_data.get('confirm'):
                    topic = message['topic']
                    kline = [
                        kline_data['start'],
                        float(kline_data['open']),
                        float(kline_data['high']),
                        float(kline_data['low']),
                        float(kline_data['close']),
                        float(kline_data['volume'])
                    ]
                    self.on_kline({'topic': topic, 'kline': kline})
        except (KeyError, IndexError, ValueError) as e:
            self.logger.warning(
                f'Unexpected message format: {e} | raw: {message}'
            )