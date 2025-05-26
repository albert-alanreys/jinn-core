from logging import getLogger

import config
from src.services.automation.api_clients.http_client import HttpClient


class TelegramClient(HttpClient):
    def __init__(self) -> None:
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat = config.TELEGRAM_CHAT_ID

        self.logger = getLogger(__name__)

    def notify(self, msg: dict) -> None:
        try:
            message = (
                f"Биржа — {msg['message']['exchange']}\n"
                f"Тип — {msg['message']['type']}\n"
                f"Статус — {msg['message']['status']}\n"
                f"Направление — {msg['message']['side']}\n"
                f"Символ — #{msg['message']['symbol']}\n"
                f"Количество — {msg['message']['qty']}\n"
                f"Цена — {msg['message']['price']}"
            )
            self._send_message(message)
        except Exception as e:
            self.logger.error(f'{type(e).__name__}: {str(e)}')

    def _send_message(self, message: str) -> None:
        params = {
            'chat_id': self.chat,
            'text': message,
        }

        self.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=params
        )