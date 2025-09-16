from __future__ import annotations
from hashlib import sha256
from hmac import new
from time import time

from src.infrastructure.transport import HttpClient


class BaseBinanceClient(HttpClient):
    """
    Base client for Binance API operations.

    Provides common functionality for all Binance API clients including
    authentication, request signing, and endpoint configuration.
    """

    BASE_ENDPOINT = 'https://fapi.binance.com'

    def __init__(self, api_key: str, api_secret: str) -> None:
        """
        Initialize base client with API credentials.  
        Stores credentials for use in request headers and signing.
        
        Args:
            api_key: Binance API key for authentication
            api_secret: Binance API secret for request signing
        """

        self.api_key = api_key
        self.api_secret = api_secret

    def build_signed_request(self, params: dict) -> tuple:
        """
        Build signed request parameters and headers
        for authenticated API calls.

        Adds receive window, timestamp, and signature to parameters.
        Creates authentication headers with API key.

        Args:
            params: Request parameters to be signed

        Returns:
            tuple: (signed_params, headers) ready for API request
        """

        params['recvWindow'] = 5000
        params['timestamp'] = int(time() * 1000)
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        return params, headers

    def _add_signature(self, params: dict) -> dict:
        """
        Add HMAC SHA256 signature to request parameters.
        
        Creates query string from parameters and signs it
        with API secret using HMAC SHA256 algorithm.

        Args:
            params: Parameters to sign

        Returns:
            dict: Parameters with signature added
        """

        str_to_sign = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=sha256
        ).hexdigest()
        params['signature'] = signature
        return params