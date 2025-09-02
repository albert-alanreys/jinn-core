from __future__ import annotations
from enum import Enum
from typing import TypedDict


class Exchange(Enum):
    """Supported cryptocurrency exchanges."""

    BINANCE = 'Binance'
    BYBIT = 'Bybit'


class Interval(Enum):
    """Supported kline intervals."""
    
    MIN_1 = '1 Min'
    MIN_5 = '5 Min'
    MIN_15 = '15 Min'
    MIN_30 = '30 Min'
    HOUR_1 = '1 Hour'
    HOUR_2 = '2 Hours'
    HOUR_4 = '4 Hours'
    HOUR_6 = '6 Hours'
    HOUR_12 = '12 Hours'
    DAY_1 = '1 Day'


class Alert(TypedDict):
    """Configuration schema for alert."""
    
    exchange: str
    type: str
    status: str
    side: str
    symbol: str
    qty: str
    price: str
    time: str