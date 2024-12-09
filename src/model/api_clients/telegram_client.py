import logging
import requests

import config


class TelegramClient():
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

    def send_message(self, msg: str) -> None:
        try:
            requests.post(self.url, {'chat_id': self.chat, 'text': msg})
        except Exception as e:
            self.logger.error(f'Error: {e}')