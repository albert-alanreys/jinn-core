from .base import BaseBybitClient


class AccountClient(BaseBybitClient):
    """
    Client for Bybit account-related operations.

    Serves as:
    - access point to account-specific endpoints
    - storage for API credentials used by all dependent subclients
    """

    def __init__(self, api_key: str, api_secret: str) -> None:
        """
        Initialize account client with base client functionality.
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
        """

        super().__init__(api_key, api_secret)

    def get_wallet_balance(self) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/account/wallet-balance'
        params = {'accountType': 'UNIFIED', 'coin': 'USDT'}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)