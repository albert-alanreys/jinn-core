from __future__ import annotations
from typing import Any, TypedDict


class ExecutionContextResponse(TypedDict):
    """Response format for execution context data."""
    
    name: str
    exchange: str
    isLive: bool
    symbol: str
    interval: str
    minMove: float
    precision: int
    strategyParams: dict[str, Any]
    indicatorOptions: dict[str, Any]


class OptimizationContextResponse(TypedDict):
    """Response format for optimization context data."""
    
    strategy: str
    symbol: str
    interval: str
    exchange: str
    start: str
    end: str
    optimizedParams: list[dict]