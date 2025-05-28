import hmac
import json
from hashlib import sha256
from logging import getLogger
from os import getenv
from time import time

from src.services.automation.api_clients.http_client import HttpClient


class BaseClient(HttpClient):
    BASE_ENDPOINT = 'https://api.bybit.com'
    EXCHANGE = 'BYBIT'

    def __init__(self) -> None:
        self.api_key = getenv('BYBIT_API_KEY')
        self.api_secret = getenv('BYBIT_API_SECRET')
        self.logger = getLogger(__name__)

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