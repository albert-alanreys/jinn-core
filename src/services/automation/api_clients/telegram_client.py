import logging

import config
from .http_client import HttpClient


class TelegramClient(HttpClient):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.token = config.TELEGRAM_BOT_TOKEN
            self.chat = config.TELEGRAM_CHAT_ID

            self.url = f'https://api.telegram.org/bot{self.token}/sendMessage'
            self.logger = logging.getLogger(__name__)

            self._initialized = True

    def send_message(self, message: str) -> None:
        params = {'chat_id': self.chat, 'text': message}
        self.post(self.url, json=params)