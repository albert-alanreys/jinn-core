from __future__ import annotations
from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import iter_modules

from src.infrastructure.exchanges import BaseExchangeClient
from src.infrastructure.exchanges.models import Interval
from src.shared.utils import adjust

from .core import (
    BaseStrategy,
    colors,
    quanta,
    update_completed_deals_log,
    update_open_deals_log,
    remove_open_deal,
    clear_open_deals_log,
    calculate_avg_entry_price,
    calculate_total_position_size,
    count_open_deals
)


def _load_strategies() -> dict[str, type[BaseStrategy]]:
    """
    Dynamically load all strategy classes from this package.

    Returns:
        dict: Mapping from strategy class names to their class objects
    """
    
    import src.core.strategies as package

    strategy_registry: dict[str, type[BaseStrategy]] = {}

    for _, module_name, _ in iter_modules(package.__path__):
        if module_name in {'strategy', 'utils'}:
            continue

        module = import_module(f'{package.__name__}.{module_name}')

        for name, obj in getmembers(module, isclass):
            if (
                obj.__module__ == module.__name__
                and issubclass(obj, BaseStrategy)
                and obj is not BaseStrategy
            ):
                strategy_registry[name] = obj

    return strategy_registry


strategy_registry = _load_strategies()