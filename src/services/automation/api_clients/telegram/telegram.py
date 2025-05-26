from logging import getLogger

import config
from src.services.automation.api_clients.http_client import HttpClient


class TelegramClient(HttpClient):
    def __init__(self) -> None:
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat = config.TELEGRAM_CHAT_ID

        self.logger = getLogger(__name__)

    def send_order_alert(self, order_data: dict) -> None:
        try:
            data = order_data['message']
            msg = (
                f"📊 <b>Информация об ордере</b>\n"
                f"════════════════════\n"
                f"│ Биржа: <b>{data['exchange']}</b>\n"
                f"│ Тип: <b>{data['type']}</b>\n"
                f"│ Статус: <b>{data['status']}</b>\n"
                f"│ Направление: <b>{data['side']}</b>\n"
                f"│ Символ: <code>#{data['symbol']}</code>\n"
                f"│ Количество: <b>{data['qty']}</b>\n"
                f"│ Цена: <b>{data['price']}</b>\n"
                f"════════════════════\n"
                f"🕒 {order_data['time']}"
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