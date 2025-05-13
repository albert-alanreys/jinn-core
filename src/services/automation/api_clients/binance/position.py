from .base import BaseClient


class PositionClient(BaseClient):
    def set_leverage(self, symbol: str, leverage: int) -> dict:
        params = {
            'symbol': symbol,
            'leverage': leverage,
        }
        params, headers = self.build_signed_request(params)

        return self.post(
            url=f'{self.futures_endpoint}/fapi/v1/leverage',
            params=params,
            headers=headers,
            logging=False
        )

    def switch_margin_mode(self, symbol: str, mode: int) -> dict:
        params = {
            'symbol': symbol,
            'marginType': mode,
        }
        params, headers = self.build_signed_request(params)

        return self.post(
            url=f'{self.futures_endpoint}/fapi/v1/marginType',
            params=params,
            headers=headers,
            logging=False
        )

    def switch_position_mode(self, mode: bool) -> dict:
        params = {
            'dualSidePosition': mode,
        }
        params, headers = self.build_signed_request(params)

        return self.post(
            url=f'{self.futures_endpoint}/fapi/v1/positionSide/dual',
            params=params,
            headers=headers,
            logging=False
        )