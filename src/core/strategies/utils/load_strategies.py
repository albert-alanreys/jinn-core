from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import iter_modules

from src.core import strategies
from src.core.strategies.strategy import BaseStrategy


def load_strategies() -> dict[str, type[BaseStrategy]]:
    """
    Dynamically load all strategy classes from the strategies package.

    Returns:
        dict: Dictionary mapping strategy class names to their class objects
    """

    strategy_classes = {}
    package = strategies

    for _, module_name, _ in iter_modules(package.__path__):
        module = import_module(f'{package.__name__}.{module_name}')
        
        for name, obj in getmembers(module, isclass):
            if obj.__module__ == module.__name__:
                strategy_classes[name] = obj

    return strategy_classes