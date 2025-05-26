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
            data = msg['message']
            
            side_map = {
                'BUY': 'покупка',
                'SELL': 'продажа'
            }
            type_map = {
                'TAKE_PROFIT': 'лимитный ордер',
                'LIMIT': 'лимитный ордер',
                'MARKET': 'рыночный ордер',
                'STOP_MARKET': 'стоп-ордер',
                'STOP': 'стоп-ордер'
            }

            order_type = type_map.get(data['type'].upper(), data['type'])
            direction = side_map.get(data['side'].upper(), data['side'])
            
            message = (
                f"📊 <b>Информация об ордере</b>\n"
                f"┌───────────────────────\n"
                f"│ Биржа: <b>{data['exchange']}</b>\n"
                f"│ Тип: <b>{order_type}</b>\n"
                f"│ Статус: <b>{data['status']}</b>\n"
                f"│ Направление: <b>{direction}</b>\n"
                f"│ Символ: <code>#{data['symbol']}</code>\n"
                f"│ Количество: <b>{data['qty']}</b>\n"
                f"│ Цена: <b>{data['price']}</b>\n"
                f"└───────────────────────\n"
                f"🕒 {msg['time']}"
            )
            self._send_message(message)
        except Exception as e:
            self.logger.error(f'{type(e).__name__}: {str(e)}')

    def _send_message(self, msg: str) -> None:
        params = {
            'chat_id': self.chat,
            'text': msg,
            'parse_mode': 'HTML'
        }
        self.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=params
        )