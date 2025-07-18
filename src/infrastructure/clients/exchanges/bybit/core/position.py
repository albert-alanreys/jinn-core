from .base import BaseClient


class PositionClient(BaseClient):
    """
    Client for Bybit position management operations.
    
    Handles position-related settings including leverage, margin mode,
    and position mode configuration for futures trading.
    """

    def __init__(self) -> None:
        """Initialize position client with base client functionality."""

        super().__init__()

    def set_leverage(
        self,
        symbol: str,
        buy_leverage: str,
        sell_leverage: str
    ) -> dict:
        """
        Set leverage for specified symbol.
        
        Configures the leverage multiplier for futures trading on the
        specified symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., 'BTCUSDT')
            leverage (int): Leverage multiplier
        
        Returns:
            dict: API response confirming leverage setting
        """

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
        """
        Switch margin mode for specified symbol.
        
        Changes between cross margin and isolated margin modes for
        futures trading.
        
        Args:
            symbol (str): Trading symbol
            mode (str): Margin mode (0 - cross margin, 1 - isolated margin)
        
        Returns:
            dict: API response confirming margin mode change
        """

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
        """
        Switch position mode between one-way and hedge mode.
        
        Configures whether to use hedge mode (separate long/short positions)
        or one-way mode (net position).
        
        Args:
            mode (bool): True for hedge mode, False for one-way mode
            
        Returns:
            dict: API response confirming position mode change
        """

        url = f'{self.BASE_ENDPOINT}/v5/position/switch-mode'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'mode': mode
        }
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers, logging=False)