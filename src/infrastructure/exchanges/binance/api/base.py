import hmac
from hashlib import sha256
from logging import getLogger
from os import getenv
from time import time

from src.infrastructure.transport import HttpClient


class BaseBinanceClient(HttpClient):
    """
    Base client for Binance API operations.

    Provides common functionality for all Binance API clients including
    authentication, request signing, and endpoint configuration.
    """

    BASE_ENDPOINT = 'https://fapi.binance.com'

    def __init__(self) -> None:
        """
        Initialize base client with API credentials
        from environment variables.

        Reads the following environment variables:
        - BINANCE_API_KEY: API key for Binance authentication
        - BINANCE_API_SECRET: API secret for request signing
        
        Initializes:
        - api_key: Stores the Binance API key
        - api_secret: Stores the Binance API secret
        - logger: Logger instance for this module
        """

        super().__init__()

        self.api_key = getenv('BINANCE_API_KEY')
        self.api_secret = getenv('BINANCE_API_SECRET')

        self.logger = getLogger(__name__)

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
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=sha256
        ).hexdigest()
        params['signature'] = signature
        return params