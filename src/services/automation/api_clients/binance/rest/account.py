from .base import BaseClient


class AccountClient(BaseClient):
    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def get_wallet_balance(self) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v3/account'
        params, headers = self.build_signed_request({})
        return self.get(url, params, headers)