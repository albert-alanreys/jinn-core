from typing import Any

from src.core.utils.singleton import singleton
from .account import AccountClient
from .market import MarketClient
from .position import PositionClient
from .trade import TradeClient


@singleton
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
        for subclient_name in ('account', 'market', 'position', 'trade'):
            try:
                subclient = object.__getattribute__(self, subclient_name)
                return getattr(subclient, name)
            except AttributeError:
                continue

        raise AttributeError(f'BybitClient has no attribute "{name}"')