from logging import getLogger
from queue import Queue

from .connection import WebSocketConnection


class KlineStream:
    BASE_ENDPOINT = 'wss://stream.bybit.com/v5/public/linear'

    def __init__(self) -> None:
        self.queue = Queue()
        self.ws = WebSocketConnection(self.BASE_ENDPOINT)

        self.logger = getLogger(__name__)

    def get_topic(self, interval: str, symbol: str) -> str:
        return f'kline.{interval}.{symbol}'
    
    def get_queue(self) -> Queue:
        return self.queue

    def start_stream(self, topics: list) -> None:
        payload = {
            'req_id': 'subscribe',
            'op': 'subscribe',
            'args': topics
        }
        self.ws.listen(self._on_message, payload)

    def _on_message(self, message: dict) -> None:
        if 'data' in message:
            kline_data = message['data'][0]

            if kline_data.get('confirm'):
                self.queue.put(kline_data)
