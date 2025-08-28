from __future__ import annotations
from typing import TypedDict


class ExecutionContextResponse(TypedDict):
    """Response format for execution context data."""
    
    strategy: str
    symbol: str
    interval: str
    exchange: str
    isLive: bool
    minMove: float
    precision: int
    params: dict[str, bool | int | float]


class OptimizationContextResponse(TypedDict):
    """Response format for optimization context data."""
    
    strategy: str
    symbol: str
    interval: str
    exchange: str
    start: str
    end: str
    params: list[dict[str, bool | int | float]]