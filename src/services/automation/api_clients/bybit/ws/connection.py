import json
import time
from logging import getLogger
from threading import Thread, Event
from typing import Callable

from websockets.sync.client import connect


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

        self.websocket = None
        self.ping_thread = None

        self.stop_event = Event()
        self.logger = getLogger(__name__)

    def listen(self, on_message: Callable, payload: dict) -> None:
        retry_count = 0

        while True:
            try:
                with connect(self.url, ping_interval=None) as websocket:
                    self.websocket = websocket
                    self.logger.info('WebSocket connection established')

                    self._subscribe(payload)

                    self.stop_event.clear()
                    self._start_ping_thread()

                    while not self.stop_event.is_set():
                        message = websocket.recv()
                        data = json.loads(message)
                        on_message(data)
            except Exception as e:
                self.logger.warning(f'WebSocket connection lost: {e}')
                retry_count += 1

                if retry_count > self.max_retries:
                    self.logger.critical('Max retries exceeded, giving up')
                    break

                self.logger.info(f'Reconnecting in {self.retry_delay}s')
                time.sleep(self.retry_delay)
            finally:
                self.stop_event.set()

                if self.ping_thread is not None:
                    self.ping_thread.join(timeout=1.0)

                self.websocket = None
                self.ping_thread = None

    def _subscribe(self, payload: dict) -> None:
        try:
            self.websocket.send(json.dumps(payload))
            self.logger.info(
                f'WebSocket subscribed:\n'
                f'{" | ".join(payload["args"])}'
            )
        except Exception as e:
            self.logger.error(f'Failed to send subscription payload: {e}')
            raise

    def _start_ping_thread(self) -> None:
        def ping():
            while not self.stop_event.wait(10):
                try:
                    if self.websocket is not None:
                        self.websocket.send(json.dumps({'op': 'ping'}))
                    else:
                        break
                except Exception:
                    pass

        self.ping_thread = Thread(target=ping, daemon=True)
        self.ping_thread.start()