from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

import numpy as np

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient
    from src.infrastructure.exchanges.models import Alert


class ContextStatus(Enum):
    """Strategy context lifecycle status."""
    
    QUEUED = 'queued'
    CREATING = 'creating'
    READY = 'ready'
    FAILED = 'failed'


class ContextConfig(TypedDict):
    """Configuration schema for strategy execution context."""

    strategy: str
    symbol: str
    interval: str
    exchange: str
    is_live: bool
    params: dict[str, Any]

    start: NotRequired[str]
    end: NotRequired[str]


class AlertData(TypedDict):
    """Trading alert notification data."""
    
    context_id: str
    strategy: str
    message: Alert


class Metric(TypedDict):
    """Individual strategy performance metric."""
    
    title: str
    all: list[float | int]
    long: list[float | int]
    short: list[float | int]


class OverviewMetrics(TypedDict):
    """High-level strategy overview metrics.."""

    primary: list[Metric]
    equity: np.ndarray


class StrategyMetrics(TypedDict):
    """Complete set of strategy performance metrics."""

    overview: OverviewMetrics
    performance: list[Metric]
    trades: list[Metric]
    risk: list[Metric]


class StrategyContext(TypedDict):
    """Complete strategy execution context."""
    
    name: str
    exchange: str
    is_live: bool
    strategy: BaseStrategy
    client: BaseExchangeClient
    market_data: MarketData
    metrics: StrategyMetrics