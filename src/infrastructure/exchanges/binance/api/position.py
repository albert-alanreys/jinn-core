from logging import getLogger
from typing import TYPE_CHECKING

from src.shared.utils import adjust
from .base import BaseBinanceClient

if TYPE_CHECKING:
    from .account import AccountClient
    from .market import MarketClient


class PositionClient(BaseBinanceClient):
    """
    Client for Binance position management operations.
    
    Handles position-related settings including leverage, margin mode,
    position mode configuration for futures trading,
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
            account (AccountClient): Account client instance
            market (MarketClient): Market client instance
        """

        super().__init__()

        self.account = account
        self.market = market

        self.logger = getLogger(__name__)

    def switch_position_mode(self, mode: bool) -> dict:
        url = f'{self.BASE_ENDPOINT}/fapi/v1/positionSide/dual'
        params = {'dualSidePosition': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def switch_margin_mode(self, symbol: str, mode: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/fapi/v1/marginType'
        params = {'symbol': symbol, 'marginType': mode}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def set_leverage(self, symbol: str, leverage: int) -> dict:
        url = f'{self.BASE_ENDPOINT}/fapi/v1/leverage'
        params = {'symbol': symbol, 'leverage': leverage}
        params, headers = self.build_signed_request(params)
        return self.post(url, params=params, headers=headers, logging=False)

    def get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int,
        price: float | None = None
    ) -> float:
        effective_price = price

        if price is None:
            market_data = self.market.get_tickers(symbol)
            effective_price = float(market_data['markPrice'])

        balance_info = self.account.get_wallet_balance()['assets']
        balance = float(
            next(
                filter(
                    lambda balance: balance['asset'] == 'USDT',
                    balance_info
                )
            )['availableBalance']
        )

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
        hedge: bool,
        price: float | None = None
    ) -> float:
        position_size = self._get_position_size(side, symbol, hedge)

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = position_size * size_val * 0.01
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            effective_price = price

            if price is None:
                market_data = self.market.get_tickers(symbol)
                effective_price = float(market_data['markPrice'])

            qty = size_val / effective_price

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def _get_position_size(
        self,
        side: str,
        symbol: str,
        hedge: bool
    ) -> float:
        """
        Internal method to get current position size for specified side.
        
        Retrieves the current position amount for the specified
        side and symbol, considering hedge mode settings.
        
        Args:
            side (str): Position side ('LONG' or 'SHORT')
            symbol (str): Trading symbol
            hedge (bool): Use hedge mode for position
            
        Returns:
            float: Current position size
                   (positive for long, negative for short)
        """

        try:
            positions = self._get_positions(symbol)
            multiplier = 1 if side == 'LONG' else -1
            position_side = side if hedge else 'BOTH'
            position = next(
                filter(
                    lambda pos: pos['positionSide'] == position_side,
                    positions
                )
            )
            return multiplier * float(position['positionAmt'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> list:
        """
        Internal method to retrieve position information via API.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            list: Position information from API
        """

        url = f'{self.BASE_ENDPOINT}/fapi/v3/positionRisk'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)