import config
from src.core.utils.singleton import singleton
from src.services.automation.api_clients.http_client import HttpClient


@singleton
class TelegramClient(HttpClient):
    def __init__(self) -> None:
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat = config.TELEGRAM_CHAT_ID

    def send_message(self, message: str) -> None:
        params = {
            'chat_id': self.chat,
            'text': message,
        }

        self.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=params
        )