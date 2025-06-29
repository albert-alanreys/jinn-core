from logging import getLogger
from os import getenv

from src.services.automation.api_clients.http_client import HttpClient


class TelegramClient(HttpClient):
    def __init__(self) -> None:
        self.token = getenv('TELEGRAM_BOT_TOKEN')
        self.chat = getenv('TELEGRAM_CHAT_ID')
        self.logger = getLogger(__name__)

    def send_order_alert(self, alert: dict) -> None:
        try:
            msg = (
                f"📊 <b>Информация об ордере</b>\n"
                f"════════════════════\n"
                f"│ Биржа: <b>{alert['exchange']}</b>\n"
                f"│ Тип: <b>{alert['type']}</b>\n"
                f"│ Статус: <b>{alert['status']}</b>\n"
                f"│ Направление: <b>{alert['side']}</b>\n"
                f"│ Символ: <code>#{alert['symbol']}</code>\n"
                f"│ Количество: <b>{alert['qty']}</b>\n"
                f"│ Цена: <b>{alert['price']}</b>\n"
                f"════════════════════\n"
                f"🕒 {alert['time']}"
            )
            self.send_message(msg)
        except Exception as e:
            self.logger.error(f'{type(e).__name__}: {str(e)}')

    def send_message(self, msg: str) -> None:
        params = {
            'chat_id': self.chat,
            'text': msg,
            'parse_mode': 'HTML'
        }
        self.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=params,
            logging=False
        )