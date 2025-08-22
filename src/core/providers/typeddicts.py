from typing import TypedDict, NotRequired
import numpy as np

from src.infrastructure.exchanges.enums import Interval


class FeedsData(TypedDict):
    """Typed dictionary for feeds data."""

    klines: dict[str, np.ndarray]
    raw_klines: NotRequired[dict[str, np.ndarray]]


class MarketData(TypedDict):
    """Typed dictionary for market data."""
    
    symbol: str
    interval: Interval
    p_precision: float
    q_precision: float
    klines: np.ndarray
    
    feeds: NotRequired[FeedsData]
    start: NotRequired[str]
    end: NotRequired[str]