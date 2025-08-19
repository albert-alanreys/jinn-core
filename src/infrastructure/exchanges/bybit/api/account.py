from .base import BaseBybitClient


class AccountClient(BaseBybitClient):
    """
    Client for Bybit account-related operations.
    Provides information about the wallet balance.
    """

    def __init__(self) -> None:
        """Initialize account client with base client functionality."""

        super().__init__()

    def get_wallet_balance(self) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/account/wallet-balance'
        params = {'accountType': 'UNIFIED', 'coin': 'USDT'}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)