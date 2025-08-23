from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import iter_modules

from .core import BaseStrategy
from .core import update_completed_deals_log


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


strategies = _load_strategies()