from typing import TypedDict, Any, NotRequired, TYPE_CHECKING

from numpy import ndarray

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient


class ContextConfig(TypedDict):
    """Configuration for strategy execution context."""

    strategy: str
    symbol: str
    interval: str
    exchange: str
    params: dict[str, Any]
    is_live: bool

    start: NotRequired[str]
    end: NotRequired[str]


class Metric(TypedDict):
    """Typed dictionary for strategy metric."""
    
    title: str
    all: list[float | int]
    long: list[float | int]
    short: list[float | int]


class OverviewMetrics(TypedDict):
    """Typed dictionary for overview metrics."""

    primary: list[Metric]
    equity: ndarray


class StrategyMetrics(TypedDict):
    """Typed dictionary for strategy metrics."""

    overview: OverviewMetrics
    performance: list[Metric]
    trades: list[Metric]
    risk: list[Metric]


class StrategyContext(TypedDict):
    """Typed dictionary for strategy context."""
    
    name: str
    strategy: 'BaseStrategy'
    client: 'BaseExchangeClient'
    market_data: 'MarketData'
    metrics: StrategyMetrics