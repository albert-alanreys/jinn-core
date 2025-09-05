from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, NotRequired, TypedDict

import numpy as np

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient


class ContextStatus(Enum):
    """Strategy context lifecycle status."""
    
    QUEUED = 'QUEUED'
    CREATING = 'CREATING'
    READY = 'READY'
    FAILED = 'FAILED'


class ContextConfig(TypedDict):
    """Configuration schema for strategy execution context."""

    strategy: str
    symbol: str
    interval: str
    exchange: str
    params: dict[str, bool | int | float]

    start: NotRequired[str]
    end: NotRequired[str]


class AlertData(TypedDict):
    """Trading alert notification data."""
    
    alert_id: str
    context_id: str
    exchange: str
    type: str
    status: str
    side: str
    symbol: str
    qty: str
    price: str
    time: str


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