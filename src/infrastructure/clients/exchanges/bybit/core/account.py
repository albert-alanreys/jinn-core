from .base import BaseClient


class AccountClient(BaseClient):
    """
    Client for Bybit account-related operations.
    Provides information about the wallet balance.
    """

    def __init__(self) -> None:
        """Initialize account client with base client functionality."""

        super().__init__()

    def get_wallet_balance(self) -> dict:
        """
        Retrieve wallet balance information for unified account.
        
        Returns:
            dict: Account balance information with assets array
        """

        url = f'{self.BASE_ENDPOINT}/v5/account/wallet-balance'
        params = {'accountType': 'UNIFIED', 'coin': 'USDT'}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)