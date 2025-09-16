from __future__ import annotations
from hashlib import sha256
from hmac import new
from json import dumps
from time import time

from src.infrastructure.transport import HttpClient


class BaseBybitClient(HttpClient):
    """
    Base client for ByBit API operations.
    
    Provides common functionality for all ByBit API clients including
    authentication, request signing, and endpoint configuration.
    """

    BASE_ENDPOINT = 'https://api.bybit.com'

    def __init__(self, api_key: str, api_secret: str) -> None:
        """
        Initialize base client with API credentials.  
        Stores credentials for use in request headers and signing.
        
        Args:
            api_key: Bybit API key for authentication
            api_secret: Bybit API secret for request signing
        """

        self.api_key = api_key
        self.api_secret = api_secret

    def get_headers(self, params: dict, method: str) -> dict:
        """
        Generate authenticated headers for ByBit API requests.
        
        Creates required authentication headers including timestamp,
        signature, and API key based on request parameters and method.
        
        Args:
            params: Request parameters
            method: HTTP method ('GET' or 'POST')
            
        Returns:
            dict: Complete headers dictionary with authentication
        """

        timestamp = str(int(time() * 1000))
        recv_window = '5000'

        match method:
            case 'GET':
                query_str = '&'.join(f'{k}={v}' for k, v in params.items())
            case 'POST':
                query_str = dumps(params)

        str_to_sign = f'{timestamp}{self.api_key}{recv_window}{query_str}'
        signature = new(
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