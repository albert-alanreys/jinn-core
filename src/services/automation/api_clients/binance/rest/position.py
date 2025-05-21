from .base import BaseClient


class PositionClient(BaseClient):
    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def set_leverage(self, symbol: str, leverage: int) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/leverage'
        params = {'symbol': symbol, 'leverage': leverage}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def switch_margin_mode(self, symbol: str, mode: int) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/marginType'
        params = {'symbol': symbol, 'marginType': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def switch_position_mode(self, mode: bool) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/positionSide/dual'
        params = {'dualSidePosition': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)