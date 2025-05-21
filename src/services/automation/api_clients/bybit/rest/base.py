import hmac
import json
from datetime import datetime, timezone
from hashlib import sha256
from time import time

import config
from src.core.enums import Exchange
from src.services.automation.api_clients.http_client import HttpClient
from src.services.automation.api_clients.telegram import TelegramClient


class BaseClient(HttpClient):
    exchange = Exchange.BYBIT
    base_endpoint = 'https://api.bybit.com'
    # base_endpoint = 'https://api-testnet.bybit.com'

    def __init__(self, alerts: list) -> None:
        self.telegram = TelegramClient()

        self.alerts = alerts
        self.api_key = config.BYBIT_API_KEY
        self.api_secret = config.BYBIT_API_SECRET
        
    def get_headers(self, params: dict, method: str) -> dict:
        timestamp = str(int(time() * 1000))
        recv_window = '5000'

        match method:
            case 'GET':
                query_str = '&'.join(f'{k}={v}' for k, v in params.items())
            case 'POST':
                query_str = json.dumps(params)

        str_to_sign = f'{timestamp}{self.api_key}{recv_window}{query_str}'
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=sha256
        ).hexdigest()
        
        return {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-SIGN': signature,
            'X-BAPI-RECV-WINDOW': recv_window,
        }

    def send_exception(self, exception: Exception) -> None:
        if exception:
            self.alerts.append({
                'message': {
                    'exchange': 'BYBIT',
                    'error': str(exception)
                },
                'time': datetime.now(
                    timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{'BYBIT'}:\n{exception}'
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