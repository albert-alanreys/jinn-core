from abc import ABC, abstractmethod


class TradeClientInterface(ABC):
    """Interface for trading operations."""
    
    @abstractmethod
    def market_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        """
        Open long position with market order.
        
        Places market buy order to open long position with specified
        size, margin mode, and leverage settings.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            hedge (bool): Use hedge mode for position
        """
        pass

    @abstractmethod
    def market_open_short(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        """
        Open short position with market order.
        
        Places market sell order to open short position with specified
        size, margin mode, and leverage settings.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            hedge (bool): Use hedge mode for position
        """
        pass

    @abstractmethod
    def market_close_long(self, symbol: str, size: str, hedge: bool) -> None:
        """
        Close long position with market order.
        
        Places market sell order to close existing long position.
        Supports partial closing with size specification.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            hedge (bool): Use hedge mode for position
        """
        pass

    @abstractmethod
    def market_close_short(self, symbol: str, size: str, hedge: bool) -> None:
        """
        Close short position with market order.
        
        Places market buy order to close existing short position.
        Supports partial closing with size specification.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            hedge (bool): Use hedge mode for position
        """
        pass

    @abstractmethod
    def market_stop_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Place stop-loss order to close long position.
        
        Creates stop-market order that will trigger when price falls
        to specified level, closing the long position.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Stop price trigger level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created stop order
        """
        pass

    @abstractmethod
    def market_stop_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Place stop-loss order to close short position.
        
        Creates stop-market order that will trigger when price rises
        to specified level, closing the short position.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Stop price trigger level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created stop order
        """
        pass

    @abstractmethod
    def limit_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
        hedge: bool
    ) -> int:
        """
        Open long position with limit order.
        
        Places limit buy order to open long position at specified price
        with configured margin mode and leverage.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            price (float): Limit order price
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created limit order
        """
        pass

    @abstractmethod
    def limit_open_short(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
        hedge: bool
    ) -> int:
        """
        Open short position with limit order.
        
        Places limit sell order to open short position at specified price
        with configured margin mode and leverage.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            price (float): Limit order price
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created limit order
        """
        pass

    @abstractmethod
    def limit_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Close long position with limit order (take profit).
        
        Places take-profit order to close long position when price
        reaches specified level.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Take profit price level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created take profit order
        """
        pass

    @abstractmethod
    def limit_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Close short position with limit order (take profit).
        
        Places take-profit order to close short position when price
        reaches specified level.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Take profit price level
            hedge (bool): Use hedge mode for position
        
        Returns:
            int: Order ID of created take profit order
        """
        pass

    @abstractmethod
    def cancel_all_orders(self, symbol: str) -> None:
        """
        Cancel all open orders for specified symbol.
        
        Cancels all pending orders (limit, stop, etc.) for the symbol
        across all position sides.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
        """
        pass

    @abstractmethod
    def cancel_orders(self, symbol: str, side: str) -> None:
        """
        Cancel all orders for specified symbol and side.
        
        Cancels all pending orders matching the specified side
        (buy or sell) for the symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            side (str): Order side ('buy' or 'sell')
        """
        pass

    @abstractmethod
    def cancel_limit_orders(self, symbol: str, side: str) -> None:
        """
        Cancel limit orders for specified symbol and side.
        
        Cancels only limit orders matching the specified side
        for the symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            side (str): Order side ('buy' or 'sell')
        """
        pass

    @abstractmethod
    def cancel_stop_orders(self, symbol: str, side: str) -> None:
        """
        Cancel stop orders for specified symbol and side.
        
        Cancels only stop-market orders matching the specified side
        for the symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            side (str): Order side ('buy' or 'sell')
        """
        pass

    @abstractmethod
    def check_stop_orders(self, symbol: str, order_ids: list) -> list:
        """
        Check status of stop orders and update alerts.
        
        Monitors stop orders for status changes (filled, cancelled) and
        creates appropriate alerts. Returns list of still active orders.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            order_ids (list): List of order IDs to check
            
        Returns:
            list: List of order IDs that are still active
        """
        pass

    @abstractmethod
    def check_limit_orders(self, symbol: str, order_ids: list) -> list:
        """
        Check status of limit orders and update alerts.
        
        Monitors limit orders for status changes (filled, cancelled) and
        creates appropriate alerts. Returns list of still active orders.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            order_ids (list): List of order IDs to check
            
        Returns:
            list: List of order IDs that are still active
        """
        pass