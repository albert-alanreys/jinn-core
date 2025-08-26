from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy


class ContextStatus(Enum):
    """Strategy context lifecycle status."""
    
    QUEUED = 'queued'
    CREATING = 'creating'
    OPTIMIZATION = 'optimization'
    READY = 'ready'
    FAILED = 'failed'


class ContextConfig(TypedDict):
    """Configuration schema for strategy optimization context."""

    strategy: str
    symbol: str
    interval: str
    exchange: str
    start: str
    end: str


class StrategyContext(TypedDict):
    """Complete strategy optimization context."""
    
    context_config: ContextConfig
    market_data: MarketData
    strategy_class: BaseStrategy
    opt_params: list[dict[str, Any]]