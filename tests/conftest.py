from __future__ import annotations
from typing import TYPE_CHECKING

from pytest import fixture

from src.core.strategies import strategy_registry
from src.features.execution import ExecutionService
from src.features.optimization import OptimizationService

from .enums import Mode
from .templates import (
    backtesting_config_template,
    optimization_config_template
)

if TYPE_CHECKING:
    from src.features.execution.models import (
        ContextConfig as ExecutionContextConfig
    )
    from src.features.optimization.models import (
        ContextConfig as OptimizationContextConfig
    )


def pytest_addoption(parser):
    parser.addoption(
        '--mode',
        action='store',
        choices=[mode.name[0].lower() for mode in Mode],
        help=(
            'Choose test mode: '
            'o=optimization, b=backtesting, l=live trading, f=full pipeline'
        )
    )

    parser.addoption(
        '--strategy',
        action='store',
        default=None,
        help='Run tests only for a specific strategy by name'
    )


def pytest_collection_modifyitems(config, items):
    mode = config.getoption('--mode')
    
    if not mode:
        return
    
    mode_enum = Mode.from_short(mode)
    selected, deselected = [], []

    for item in items:
        if mode_enum.value in item.name.lower():
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@fixture(scope='session')
def strategy_name(pytestconfig):
    return pytestconfig.getoption('strategy')


@fixture(scope='session')
def backtesting_config(strategy_name) -> ExecutionContextConfig:
    config = backtesting_config_template.copy()

    if strategy_name:
        try:
            strategy_cls = strategy_registry[strategy_name]
        except KeyError:
            raise KeyError(
                f"Strategy '{strategy_name}' not found in registry"
            )

        config['strategy'] = strategy_name
        config['params'] = strategy_cls.get_params()
    
    return config


@fixture(scope='session')
def optimization_config(strategy_name) -> OptimizationContextConfig:
    config = optimization_config_template.copy()

    if strategy_name not in strategy_registry:
        raise KeyError(f"Strategy '{strategy_name}' not found in registry")

    config['strategy'] = strategy_name
    return config


@fixture(scope='session')
def execution_service() -> ExecutionService:
    return ExecutionService()


@fixture(scope='session')
def optimization_service() -> OptimizationService:
    return OptimizationService()