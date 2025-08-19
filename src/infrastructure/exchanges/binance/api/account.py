from .base import BaseBinanceClient


class AccountClient(BaseBinanceClient):
    """
    Client for Binance account-related operations.
    Provides information about the wallet balance.
    """

    def __init__(self) -> None:
        """Initialize account client with base client functionality."""

        super().__init__()

    def get_wallet_balance(self) -> dict:
        url = f'{self.BASE_ENDPOINT}/fapi/v3/account'
        params, headers = self.build_signed_request({})
        return self.get(url, params, headers)