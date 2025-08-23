from enum import Enum
from typing import TypedDict


class Exchange(Enum):
    """
    Supported cryptocurrency exchanges.
    
    Attributes:
        BINANCE: Binance exchange
        BYBIT: Bybit exchange
    """

    BINANCE = 'BINANCE'
    BYBIT = 'BYBIT'


class Interval(Enum):
    """
    Supported kline intervals.
    
    Attributes:
        MIN_1: 1 minute interval
        MIN_5: 5 minutes interval
        MIN_15: 15 minutes interval
        MIN_30: 30 minutes interval
        HOUR_1: 1 hour interval
        HOUR_2: 2 hours interval
        HOUR_4: 4 hours interval
        HOUR_6: 6 hours interval
        HOUR_12: 12 hours interval
        DAY_1: 1 day interval
    """
    
    MIN_1 = '1m'
    MIN_5 = '5m'
    MIN_15 = '15m'
    MIN_30 = '30m'
    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    HOUR_12 = '12h'
    DAY_1 = '1d'


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