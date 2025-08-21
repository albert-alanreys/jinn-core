from logging import getLogger
from typing import TYPE_CHECKING

from src.shared.utils import adjust
from .base import BaseBybitClient

if TYPE_CHECKING:
    from .account import AccountClient
    from .market import MarketClient


class PositionClient(BaseBybitClient):
    """
    Client for Bybit position management operations.
    
    Handles position-related settings including leverage,
    margin mode, position mode configuration,
    and position size calculations.
    """

    def __init__(
        self,
        account: 'AccountClient',
        market: 'MarketClient'
    ) -> None:
        """
        Initialize position client with required dependencies.
        
        Args:
            account: Account client instance
            market: Market client instance
        """

        super().__init__()

        self.account = account
        self.market = market

        self.logger = getLogger(__name__)

    def switch_position_mode(self, symbol: str, mode: int) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/position/switch-mode'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'mode': mode
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
    
    def get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int,
        price: float | None = None
    ) -> float:
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

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str,
        price: float | None = None
    ) -> float:
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

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def _get_position_size(self, side: str, symbol: str) -> float:
        """
        Get current position size for specified side.
        
        Retrieves the current position amount
        for the specified side and symbol.
        
        Args:
            side: Position side ('buy' or 'sell')
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            float: Current position size
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
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            list: Position information from API
        """

        url = f'{self.BASE_ENDPOINT}/v5/position/list'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)