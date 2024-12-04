from enum import Enum


class Mode(Enum):
    AUTOMATION = 'AUTOMATION'
    INGESTION = 'INGESTION'
    OPTIMIZATION = 'OPTIMIZATION'
    TESTING = 'TESTING'


class Exchange(Enum):
    BINANCE = 'BINANCE'
    BYBIT = 'BYBIT'


class Market(Enum):
    SPOT = 'SPOT'
    FUTURES = 'FUTURES'


class BinanceInterval(Enum):
    MIN_1 = '1m'
    MIN_30 = '30m'
    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    DAY_1 = '1d'


class BybitInterval(Enum):
    MIN_1 = 1
    MIN_30 = 30
    HOUR_1 = 60
    HOUR_2 = 120
    HOUR_4 = 240
    HOUR_6 = 360
    HOUR_12 = 720
    DAY_1 = 'D'