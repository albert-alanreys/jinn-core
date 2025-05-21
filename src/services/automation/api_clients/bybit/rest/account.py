from .base import BaseClient


class AccountClient(BaseClient):
    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def get_wallet_balance(self) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/account/wallet-balance'
        params = {'accountType': 'UNIFIED', 'coin': 'USDT'}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)