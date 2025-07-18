from logging import getLogger
from typing import TYPE_CHECKING

from src.core.enums import Market
from src.utils.rounding import adjust
from .base import BaseClient

if TYPE_CHECKING:
    from .account import AccountClient
    from .market import MarketClient


class PositionClient(BaseClient):
    """
    Client for Bybit position management operations.
    
    Handles position-related settings including leverage, margin mode,
    position mode configuration for futures trading,
    and position size calculations.

    Instance Attributes:
        account (AccountClient): Account client
        market (MarketClient): Market client
        logger: Logger instance for this module
    """

    def __init__(
        self,
        account: 'AccountClient',
        market: 'MarketClient'
    ) -> None:
        """
        Initialize position client with required dependencies.
        
        Args:
            account (AccountClient): Account client instance
            market (MarketClient): Market client instance
        """

        super().__init__()

        self.account = account
        self.market = market

        self.logger = getLogger(__name__)

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
    
    def get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int,
        price: float | None = None
    ) -> float:
        """
        Calculate quantity needed to open position.
        
        Determines the quantity to open based on account balance,
        requested size, and leverage settings.
        
        Args:
            symbol (str): Trading symbol
            size (str): Position size ('10%', '100u', etc.)
            leverage (int): Leverage multiplier
            price (float | None): Price for quantity calculation
            
        Returns:
            float: Quantity to open (adjusted for precision)
        """

        effective_price = price

        if price is None:
            market_data = self.market.get_tickers(symbol)['result']['list'][0]
            effective_price = float(market_data['lastPrice'])

        wallet_data = self.account.get_wallet_balance()['result']['list']
        balance = float(wallet_data[0]['coin'][0]['walletBalance'])

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = balance * leverage * size_val * 0.01 / effective_price
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            qty = leverage * size_val / effective_price

        q_precision = self.market.get_qty_precision(
            market=Market.FUTURES,
            symbol=symbol
        )
        return adjust(qty, q_precision)

    def get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str,
        price: float | None = None
    ) -> float:
        """
        Calculate quantity needed to close position.
        
        Determines the quantity to close based on current position size
        and requested close amount (percentage or absolute value).
        
        Args:
            side (str): Position side ('buy' or 'sell')
            symbol (str): Trading symbol
            size (str): Close amount ('100%', '50u', etc.)
            price (float | None): Price for USDT-based size calculation
            
        Returns:
            float: Quantity to close (adjusted for precision)
        """

        position_size = self._get_position_size(side, symbol)

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = position_size * size_val * 0.01
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            effective_price = price

            if price is None:
                market_data = (
                    self.market.get_tickers(symbol)['result']['list'][0]
                )
                effective_price = float(market_data['lastPrice'])

            qty = size_val / effective_price

        q_precision = self.market.get_qty_precision(
            market=Market.FUTURES,
            symbol=symbol
        )
        return adjust(qty, q_precision)

    def _get_position_size(self, side: str, symbol: str) -> float:
        """
        Get current position size for specified side.
        
        Retrieves the current position amount
        for the specified side and symbol.
        
        Args:
            side (str): Position side ('buy' or 'sell')
            symbol (str): Trading symbol
            
        Returns:
            float: Current position size
                   (positive for long, negative for short)
        """

        try:
            positions = self._get_positions(symbol)['result']['list']
            position = next(
                filter(lambda pos: pos['side'] == side, positions)
            )
            return float(position['size'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> dict:
        """
        Internal method to retrieve position information via API.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            list: Position information from API
        """

        url = f'{self.BASE_ENDPOINT}/v5/position/list'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)