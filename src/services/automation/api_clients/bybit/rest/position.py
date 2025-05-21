from .base import BaseClient


class PositionClient(BaseClient):
    def __init__(self, alerts: list) -> None:
        super().__init__(alerts)

    def set_leverage(
        self,
        symbol: str,
        buy_leverage: str,
        sell_leverage: str
    ) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/position/set-leverage'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'buyLeverage': buy_leverage,
            'sellLeverage': sell_leverage
        }
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers, logging=False)

    def switch_margin_mode(self, symbol: str, mode: int) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/position/switch-isolated'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'tradeMode': mode,
            'buyLeverage': '1',
            'sellLeverage': '1'

        }
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers, logging=False)

    def switch_position_mode(self, symbol: str, mode: int) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/position/switch-mode'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'mode': mode
        }
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers, logging=False)