from typing import Any

from .core import AccountClient
from .core import MarketClient
from .core import PositionClient
from .core import TradeClient


class BybitClient():
    """
    Main Bybit client providing unified access to all trading operations.
    
    Orchestrates account, market, position, and trade clients to provide
    a comprehensive trading interface. Implements method delegation to
    allow direct access to all subclient methods.
    
    Instance Attributes:
        alerts (list): Shared list for storing trading alerts
        account (AccountClient): Account operations client
        market (MarketClient): Market data client
        position (PositionClient): Position management client
        trade (TradeClient): Trading operations client
    """

    def __init__(self) -> None:
        """
        Initialize Bybit client with all subclients.
        
        Creates instances of all required clients and establishes
        dependencies between them for seamless operation.
        """

        self.alerts = []

        self.account = AccountClient()
        self.market = MarketClient()
        self.position = PositionClient(
            account=self.account,
            market=self.market
        )
        self.trade = TradeClient(
            account=self.account,
            market=self.market,
            position=self.position,
            alerts=self.alerts
        )

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to appropriate subclient.
        
        Allows direct access to methods from account, market, position,
        and trade clients without explicit subclient reference.
        
        Args:
            name (str): Attribute/method name to access
        
        Returns:
            Any: Method or attribute from appropriate subclient
        
        Raises:
            AttributeError: If attribute not found in any subclient
        """

        for subclient_name in ('account', 'market', 'position', 'trade'):
            try:
                subclient = object.__getattribute__(self, subclient_name)
                return getattr(subclient, name)
            except AttributeError:
                continue

        raise AttributeError(f'BybitClient has no attribute "{name}"')