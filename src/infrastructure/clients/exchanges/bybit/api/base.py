import hmac
import json
from hashlib import sha256
from logging import getLogger
from os import getenv
from time import time

from src.infrastructure.clients.http_client import HttpClient


class BaseBybitClient(HttpClient):
    """
    Base client for ByBit API operations.
    
    Provides common functionality for all ByBit API clients including
    authentication, request signing, and endpoint configuration.
    """

    BASE_ENDPOINT = 'https://api.bybit.com'

    def __init__(self) -> None:
        """
        Initialize base client with credentials
        from environment variables.
        
        Reads the following environment variables:
        - BYBIT_API_KEY: API key for ByBit authentication
        - BYBIT_API_SECRET: API secret for request signing
        
        Initializes:
        - api_key (str): Stores the ByBit API key
        - api_secret (str): Stores the ByBit API secret
        - logger: Logger instance for this module
        """

        self.api_key = getenv('BYBIT_API_KEY')
        self.api_secret = getenv('BYBIT_API_SECRET')

        self.logger = getLogger(__name__)

    def get_headers(self, params: dict, method: str) -> dict:
        """
        Generate authenticated headers for ByBit API requests.
        
        Creates required authentication headers including timestamp,
        signature, and API key based on request parameters and method.
        
        Args:
            params (dict): Request parameters
            method (str): HTTP method ('GET' or 'POST')
            
        Returns:
            dict: Complete headers dictionary with authentication
        """

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