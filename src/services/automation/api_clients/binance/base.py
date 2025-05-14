import hashlib
import hmac
import time
from datetime import datetime, timezone

import config
from src.services.automation.api_clients.http_client import HttpClient
from src.services.automation.api_clients.telegram_client import TelegramClient


class BaseClient(HttpClient):
    futures_endpoint = 'https://fapi.binance.com'
    spot_endpoint = 'https://api.binance.com'

    def __init__(self, alerts: list) -> None:
        self.telegram = TelegramClient()

        self.alerts = alerts
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET

    def build_signed_request(self, params: dict) -> tuple:
        params['recvWindow'] = 5000
        params['timestamp'] = int(time.time() * 1000)
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        return params, headers

    def send_exception(self, exception: Exception) -> None:
        if exception:
            self.alerts.append({
                'message': {
                    'exchange': 'BINANCE',
                    'error': str(exception)
                },
                'time': datetime.now(
                    timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{'BINANCE'}:\n{exception}'
            self.send_telegram_alert(message)

    def send_telegram_alert(self, alert: dict) -> None:
        message = (
            f"Биржа — {alert['message']['exchange']}\n"
            f"Тип — {alert['message']['type']}\n"
            f"Статус — {alert['message']['status']}\n"
            f"Направление — {alert['message']['side']}\n"
            f"Символ — {alert['message']['symbol']}\n"
            f"Количество — {alert['message']['qty']}\n"
            f"Цена — {alert['message']['price']}"
        )
        self.telegram.send_message(message)

    def _add_signature(self, params: dict) -> dict:
        str_to_sign = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        params['signature'] = signature
        return params