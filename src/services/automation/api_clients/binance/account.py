from .base import BaseClient


class AccountClient(BaseClient):
    def get_wallet_balance(self) -> dict:
        params, headers = self.build_signed_request({})

        return self.get(
            url=f'{self.futures_endpoint}/fapi/v3/account',
            params=params,
            headers=headers
        )