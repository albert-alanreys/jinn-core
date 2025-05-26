from typing import Any, TYPE_CHECKING

from .rest import AccountClient
from .rest import MarketClient
from .rest import PositionClient
from .rest import TradeClient

if TYPE_CHECKING:
    from src.services.automation.api_clients.telegram import TelegramClient


class BybitREST():
    def __init__(self, telegram_client: 'TelegramClient') -> None:
        self.alerts = []

        self.account = AccountClient()
        self.market = MarketClient()
        self.position = PositionClient()
        self.trade = TradeClient(
            account=self.account,
            market=self.market,
            position=self.position,
            telegram=telegram_client,
            alerts=self.alerts
        )

    def __getattr__(self, name: str) -> Any:
        for subclient_name in ('account', 'market', 'position', 'trade'):
            try:
                subclient = object.__getattribute__(self, subclient_name)
                return getattr(subclient, name)
            except AttributeError:
                continue

        raise AttributeError(f'BybitREST has no attribute "{name}"')