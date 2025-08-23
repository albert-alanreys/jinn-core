from __future__ import annotations
from abc import ABC, abstractmethod


class PositionClientInterface(ABC):
    """Interface for position operations."""
    
    @abstractmethod
    def switch_position_mode(self, mode: bool) -> dict:
        """
        Switch position mode between one-way and hedge mode.
        
        Configures whether to use hedge mode (separate long/short positions)
        or one-way mode (net position).
        
        Args:
            mode: True for hedge mode, False for one-way mode
            
        Returns:
            dict: API response confirming position mode change
        """
        pass
    
    @abstractmethod
    def switch_margin_mode(self, symbol: str, mode: str) -> dict:
        """
        Switch margin mode for specified symbol.
        
        Changes between cross margin and isolated margin modes.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            mode: Margin mode ('CROSSED' or 'ISOLATED')
            
        Returns:
            dict: API response confirming margin mode change
        """
        pass
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> dict:
        """
        Set leverage for specified symbol.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            leverage: Leverage multiplier
        
        Returns:
            dict: API response confirming leverage setting
        """
        pass

    @abstractmethod
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
            symbol: Trading symbol (e.g., BTCUSDT)
            size: Position size ('10%', '100u', etc.)
            leverage: Leverage multiplier
            price: Price for quantity calculation
            
        Returns:
            float: Quantity to open (adjusted for precision)
        """
        pass

    @abstractmethod
    def get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int,
        price: float | None = None
    ) -> float:
        """
        Calculate quantity needed to close position.
        
        Determines the quantity to close based on current position size
        and requested close amount (percentage or absolute value).
        
        Args:
            side: Position side ('LONG' or 'SHORT')
            symbol: Trading symbol (e.g., BTCUSDT)
            size: Close amount ('100%', '50u', etc.)
            hedge: Use hedge mode for position
            price: Price for USDT-based size calculation
            
        Returns:
            float: Quantity to close (adjusted for precision)
        """
        pass