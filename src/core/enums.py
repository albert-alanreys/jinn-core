from enum import Enum

from src.strategies import DickeyFullerV1
from src.strategies import DevourerV3
from src.strategies import NuggetV2
from src.strategies import NuggetV4
from src.strategies import NuggetV5


class Mode(Enum):
    AUTOMATION = 'AUTOMATION'
    INGESTION = 'INGESTION'
    OPTIMIZATION = 'OPTIMIZATION'
    TESTING = 'TESTING'


class Exchange(Enum):
    BINANCE = 'BINANCE'
    BYBIT = 'BYBIT'


class Market(Enum):
    FUTURES = 'FUTURES'
    SPOT = 'SPOT'


class Strategy(Enum):
    DEVOURER_V3 = DevourerV3
    DICKEY_FULLER_V1 = DickeyFullerV1
    NUGGET_V2 = NuggetV2
    NUGGET_V4 = NuggetV4
    NUGGET_V5 = NuggetV5