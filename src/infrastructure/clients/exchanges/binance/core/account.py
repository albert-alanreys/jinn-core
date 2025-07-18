from .base import BaseClient


class AccountClient(BaseClient):
    """
    Client for Binance account-related operations.
    Provides information about the wallet balance.
    """

    def __init__(self) -> None:
        """Initialize account client with base client functionality."""

        super().__init__()

    def get_wallet_balance(self) -> dict:
        """
        Retrieve wallet balance information for futures account.
        
        Returns:
            dict: Account balance information with assets array
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v3/account'
        params, headers = self.build_signed_request({})
        return self.get(url, params, headers)