from typing import Any

from .account import AccountClient
from .market import MarketClient
from .position import PositionClient
from .trade import TradeClient


class BybitClient():
    def __init__(self) -> None:
        self.alerts = []

        self.account = AccountClient(self.alerts)
        self.market = MarketClient(self.alerts)
        self.position = PositionClient(self.alerts)
        self.trade = TradeClient(
            account=self.account,
            market=self.market,
            position=self.position,
            alerts=self.alerts
        )

    def __getattr__(self, name: str) -> Any:
        if hasattr(self.account, name):
            return getattr(self.account, name)

        if hasattr(self.market, name):
            return getattr(self.market, name)
        
        if hasattr(self.position, name):
            return getattr(self.position, name)
        
        if hasattr(self.trade, name):
            return getattr(self.trade, name)

        raise AttributeError(f'BybitClient has no attribute "{name}"')