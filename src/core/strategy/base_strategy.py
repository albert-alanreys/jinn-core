import copy
import inspect
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .order_cache import OrderCache
from src.core.storage.data_manager import DataManager

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceClient
    from src.services.automation.api_clients.bybit import BybitClient


class BaseStrategy(ABC):
    def __init__(
        self,
        all_params: dict | None = None,
        opt_params: dict | list | None = None
    ) -> None:
        self.params = copy.deepcopy(self.params)

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

        strategy_dir = os.path.dirname(inspect.getfile(self.__class__))
        self.cache = OrderCache(os.path.join(strategy_dir, '__cache__'))
        self.data_manager = DataManager()

        self.order_ids = None

    @abstractmethod
    def start(
        self,
        client: 'BinanceClient | BybitClient',
        market_data: dict
    ) -> None:
        pass

    @abstractmethod
    def trade(self) -> None:
        pass