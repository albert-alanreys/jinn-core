from .base import BaseClient


class PositionClient(BaseClient):
    """
    Client for Binance position management operations.
    
    Handles position-related settings including leverage, margin mode,
    and position mode configuration for futures trading.
    """

    def __init__(self) -> None:
        """Initialize position client with base client functionality."""

        super().__init__()

    def set_leverage(self, symbol: str, leverage: int) -> dict:
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

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/leverage'
        params = {'symbol': symbol, 'leverage': leverage}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def switch_margin_mode(self, symbol: str, mode: str) -> dict:
        """
        Switch margin mode for specified symbol.
        
        Changes between cross margin and isolated margin modes for
        futures trading.
        
        Args:
            symbol (str): Trading symbol
            mode (str): Margin mode ('CROSSED' or 'ISOLATED')
            
        Returns:
            dict: API response confirming margin mode change
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/marginType'
        params = {'symbol': symbol, 'marginType': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def switch_position_mode(self, mode: bool) -> dict:
        """
        Switch position mode between one-way and hedge mode.
        
        Configures whether to use hedge mode (separate long/short positions)
        or one-way mode (net position).
        
        Args:
            mode (bool): True for hedge mode, False for one-way mode
            
        Returns:
            dict: API response confirming position mode change
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/positionSide/dual'
        params = {'dualSidePosition': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)