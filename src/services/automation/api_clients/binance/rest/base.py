import hmac
from hashlib import sha256
from logging import getLogger
from time import time

import config
from src.services.automation.api_clients.http_client import HttpClient


class BaseClient(HttpClient):
    FUTURES_ENDPOINT = 'https://fapi.binance.com'
    SPOT_ENDPOINT = 'https://api.binance.com'
    EXCHANGE = 'BINANCE'

    def __init__(self) -> None:
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET

        self.logger = getLogger(__name__)

    def build_signed_request(self, params: dict) -> tuple:
        params['recvWindow'] = 5000
        params['timestamp'] = int(time() * 1000)
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        return params, headers

    def _add_signature(self, params: dict) -> dict:
        str_to_sign = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=sha256
        ).hexdigest()
        params['signature'] = signature
        return params