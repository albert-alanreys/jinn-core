from .base import BaseBinanceClient


class AccountClient(BaseBinanceClient):
    """
    Client for Binance account-related operations.

    Serves as:
    - access point to account-specific endpoints
    - storage for API credentials used by all dependent subclients
    """

    def __init__(self, api_key: str, api_secret: str) -> None:
        """
        Initialize account client with base client functionality.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """

        super().__init__(api_key, api_secret)

    def get_wallet_balance(self) -> dict:
        url = f'{self.BASE_ENDPOINT}/fapi/v3/account'
        params, headers = self.build_signed_request({})
        return self.get(url, params, headers)