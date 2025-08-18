from abc import ABC, abstractmethod


class MarketClientInterface(ABC):
    """Interface for market data operations."""
    
    @abstractmethod
    def get_historical_klines(
        self,
        symbol: str,
        interval: str | int,
        start: int,
        end: int
    ) -> list:
        """
        Retrieve historical kline data for specified time range.
        
        Fetches kline data by breaking large time ranges into smaller chunks
        and processing them concurrently for improved performance.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            interval (str | int): Kline interval (e.g., '1m', 60)
            start (int): Start time in milliseconds
            end (int): End time in milliseconds
            
        Returns:
            list: Historical kline data with OHLCV information
        """
        pass
    
    @abstractmethod
    def get_last_klines(
        self,
        symbol: str,
        interval: str | int,
        limit: int = 1000
    ) -> list:
        """
        Retrieve recent kline data for specified symbol.
        
        Fetches the most recent kline data up to the specified limit.
        For limits > 1000, uses time range chunking with concurrent requests.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            interval (str | int): Kline interval (e.g., '1m', 60)
            limit (int): Number of klines to retrieve (default: 1000)
            
        Returns:
            list: Recent kline data with OHLCV information
        """
        pass
    
    @abstractmethod
    def get_price_precision(self, symbol: str) -> float:
        """
        Get price precision (tick size) for specified symbol.
        
        Retrieves the minimum price increment for the symbol
        from exchange info. Result is cached for performance.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            
        Returns:
            float: Price precision value (tick size)
        """
        pass

    @abstractmethod
    def get_qty_precision(self, symbol: str) -> float:
        """
        Get quantity precision (step size) for specified symbol.
        
        Retrieves the minimum quantity increment for the symbol
        from exchange info. Result is cached for performance.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            
        Returns:
            float: Quantity precision value (step size)
        """
        pass

    @abstractmethod
    def get_tickers(self, symbol: str) -> dict:
        """
        Get ticker information including mark price for futures symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., BTCUSDT)
            
        Returns:
            dict: Ticker information with prices and rates
        """
        pass

    @abstractmethod
    def get_valid_interval(self, interval: str | int) -> str:
        """
        Convert interval input to valid interval format.
        
        Validates and normalizes interval input, supporting various formats
        including strings and integers.
        
        Args:
            interval (str | int): Interval in various formats
            
        Returns:
            str: Standardized interval string
            
        Raises:
            ValueError: If interval format is invalid
        """
        pass

    @abstractmethod
    def get_interval_duration(self, interval: str | int) -> int:
        """
        Get interval duration in milliseconds for valid interval.
        
        Args:
            interval (str | int): Kline interval (e.g., '1m', 60)
        
        Returns:
            int: Duration in milliseconds for valid interval
        """
        pass