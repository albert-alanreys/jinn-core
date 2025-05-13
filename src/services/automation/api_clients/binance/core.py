from .account import AccountClient
from .market import MarketClient
from .position import PositionClient
from .trade import TradeClient


class BinanceClient():
    def __init__(self) -> None:
        self.account = AccountClient()
        self.market = MarketClient()
        self.position = PositionClient()
        self.trade = TradeClient(self.account, self.market, self.position)

    def __getattr__(self, name):
        if hasattr(self.account, name):
            return getattr(self.account, name)

        if hasattr(self.market, name):
            return getattr(self.market, name)
        
        if hasattr(self.position, name):
            return getattr(self.position, name)
        
        if hasattr(self.trade, name):
            return getattr(self.trade, name)
        
        raise AttributeError(f'BinanceClient has no attribute "{name}"')