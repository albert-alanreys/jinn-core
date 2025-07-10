from typing import Any

from .core import AccountClient
from .core import MarketClient
from .core import PositionClient
from .core import TradeClient


class BinanceClient():
    def __init__(self) -> None:
        self.alerts = []

        self.account = AccountClient()
        self.market = MarketClient()
        self.position = PositionClient()
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

        raise AttributeError(f'BinanceClient has no attribute "{name}"')