import json
import time
from logging import getLogger
from threading import Thread, Event
from typing import Callable

from websockets.sync.client import connect, ClientConnection


class WebSocketConnection:
    def __init__(
        self,
        url: str,
        max_retries: int = 3,
        retry_delay: float = 5.0
    ) -> None:
        self.url = url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.stop_event = Event()
        self.logger = getLogger(__name__)

    def listen(self, on_message: Callable, payload: dict) -> None:
        retry_count = 0

        while True:
            try:
                with connect(self.url, ping_interval=None) as websocket:
                    self.logger.info('WebSocket connection established')

                    self._subscribe(websocket, payload)

                    self.stop_event.clear()
                    self._start_ping_thread(websocket)

                    while True:
                        message = websocket.recv()
                        data = json.loads(message)
                        on_message(data)
            except Exception as e:
                self.logger.warning(f'WebSocket connection lost: {e}')

                retry_count += 1
                if retry_count > self.max_retries:
                    self.logger.critical('Max retries exceeded, giving up')
                    break

                self.logger.info(
                    f'Reconnecting in {self.retry_delay} seconds'
                )
                time.sleep(self.retry_delay)
            finally:
                self.stop_event.set()

    def _subscribe(self, websocket: ClientConnection, payload: dict) -> None:
        try:
            websocket.send(json.dumps(payload))
            self.logger.info(
                f'WebSocket subscribed:\n'
                f'{" | ".join(payload["args"])}'
            )
        except Exception as e:
            self.logger.error(f'Failed to send subscription payload: {e}')
            raise

    def _start_ping_thread(self, websocket: ClientConnection) -> None:
        def ping():
            while not self.stop_event.is_set():
                time.sleep(20)

                try:
                    websocket.send(json.dumps({'op': 'ping'}))
                except Exception as e:
                    self.logger.warning(f'Ping failed: {e}')
                    continue

        Thread(target=ping, daemon=True).start()