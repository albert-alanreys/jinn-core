from __future__ import annotations
from typing import TYPE_CHECKING

from dotenv import load_dotenv
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
    """Add custom command-line options for pytest."""

    parser.addoption('--mode', action='store')
    parser.addoption('--strategy', action='store')


def pytest_collection_modifyitems(config, items):
    """
    Filter test items based on selected mode.
    
    In full_pipeline mode, both backtesting and optimization tests run.
    In specific modes, only matching tests are selected.
    
    Args:
        config: Pytest configuration object
        items: Collection of test items to filter
    """

    mode = config.getoption('--mode')
    
    if not mode:
        return
    
    mode_enum = Mode.from_short(mode)
    
    if mode_enum == Mode.FULL_PIPELINE:
        selected = [
            item for item in items 
            if 'backtesting' in item.name.lower() or
                'optimization' in item.name.lower()
        ]
        deselected = [item for item in items if item not in selected]
    else:
        selected = [
            item for item in items 
            if mode_enum.value in item.name.lower()
        ]
        deselected = [item for item in items if item not in selected]

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@fixture(scope='session', autouse=True)
def load_environment_variables():
    """Automatically load environment variables."""

    load_dotenv()


@fixture(scope='session')
def strategy_name(pytestconfig) -> str | None:
    """
    Retrieve strategy name from command-line options.
    
    Args:
        pytestconfig: Pytest configuration object
    
    Returns:
        str | None: Strategy name if provided, None otherwise
    """

    return pytestconfig.getoption('strategy')


@fixture(scope='session')
def backtesting_config(strategy_name) -> ExecutionContextConfig:
    """
    Create backtesting configuration for execution tests.
    
    Args:
        strategy_name: Name of the strategy to test
        
    Returns:
        ExecutionContextConfig: Configuration for backtesting context
        
    Raises:
        KeyError: If specified strategy is not found in registry
    """

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
    """
    Create optimization configuration for optimization tests.
    
    Args:
        strategy_name: Name of the strategy to optimize
        
    Returns:
        OptimizationContextConfig: Configuration for optimization context
        
    Raises:
        KeyError: If specified strategy is not found in registry
    """

    config = optimization_config_template.copy()

    if strategy_name not in strategy_registry:
        raise KeyError(f"Strategy '{strategy_name}' not found in registry")

    config['strategy'] = strategy_name
    return config


@fixture(scope='session')
def execution_service() -> ExecutionService:
    """
    Create execution service instance for testing.
    
    Returns:
        ExecutionService: Service for backtesting and live execution
    """

    return ExecutionService()


@fixture(scope='session')
def optimization_service() -> OptimizationService:
    """
    Create optimization service instance for testing.
    
    Returns:
        OptimizationService: Service for strategy parameter optimization
    """

    return OptimizationService()