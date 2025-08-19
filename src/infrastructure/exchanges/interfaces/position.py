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
            mode (bool): True for hedge mode, False for one-way mode
            
        Returns:
            dict: API response confirming position mode change
        """
        pass
    
    @abstractmethod
    def switch_margin_mode(self, symbol: str, mode: str) -> dict:
        """
        Switch margin mode for specified symbol.
        
        Changes between cross margin and isolated margin modes for
        futures trading.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            mode (str): Margin mode ('CROSSED' or 'ISOLATED')
            
        Returns:
            dict: API response confirming margin mode change
        """
        pass
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> dict:
        """
        Set leverage for specified symbol.
        
        Configures the leverage multiplier for futures trading
        on the specified symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            leverage (int): Leverage multiplier
        
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
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Position size ('10%', '100u', etc.)
            leverage (int): Leverage multiplier
            price (float | None): Price for quantity calculation
            
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
            side (str): Position side ('LONG' or 'SHORT')
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Close amount ('100%', '50u', etc.)
            hedge (bool): Use hedge mode for position
            price (float | None): Price for USDT-based size calculation
            
        Returns:
            float: Quantity to close (adjusted for precision)
        """
        pass