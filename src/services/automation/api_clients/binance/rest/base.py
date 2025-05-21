import hmac
from datetime import datetime, timezone
from hashlib import sha256
from time import time

import config
from src.services.automation.api_clients.http_client import HttpClient
from src.services.automation.api_clients.telegram import TelegramClient


class BaseClient(HttpClient):
    FUTURES_ENDPOINT = 'https://fapi.binance.com'
    SPOT_ENDPOINT = 'https://api.binance.com'
    EXCHANGE = 'BINANCE'

    _telegram = None

    def __init__(self, alerts: list) -> None:
        if BaseClient._telegram is None:
            BaseClient._telegram = TelegramClient()

        self.alerts = alerts
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET

    def build_signed_request(self, params: dict) -> tuple:
        params['recvWindow'] = 5000
        params['timestamp'] = int(time() * 1000)
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
        self._telegram.send_message(message)

    def _add_signature(self, params: dict) -> dict:
        str_to_sign = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=sha256
        ).hexdigest()
        params['signature'] = signature
        return params