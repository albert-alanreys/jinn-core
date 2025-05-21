import os
from abc import ABC, abstractmethod
from copy import deepcopy
from inspect import getfile
from typing import TYPE_CHECKING

from .order_cache import OrderCache

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceREST
    from src.services.automation.api_clients.bybit import BybitREST


class BaseStrategy(ABC):
    def __init__(
        self,
        client: 'BinanceREST | BybitREST',
        all_params: dict | None = None,
        opt_params: dict | list | None = None
    ) -> None:
        self.client = client
        self.params = deepcopy(self.params)

        if all_params is not None:
            for key, value in all_params.items():
                self.params[key] = value

        if opt_params is not None:
            if isinstance(opt_params, dict):
                for key, value in opt_params.items():
                    self.params[key] = value
            else:
                for key, value in zip(self.opt_params, opt_params):
                    self.params[key] = value

        strategy_dir = os.path.dirname(getfile(self.__class__))
        self.cache = OrderCache(
            base_dir=os.path.join(strategy_dir, '__cache__'),
            exchange=self.client.exchange.value
        )
        self.order_ids = None

    @abstractmethod
    def start(self, market_data: dict) -> None:
        pass

    @abstractmethod
    def trade(self) -> None:
        pass