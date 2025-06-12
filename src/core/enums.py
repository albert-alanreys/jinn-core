from enum import Enum

from src.strategies import DailyProfitV1
from src.strategies import DevourerV3
from src.strategies import MeanStrikeV1
from src.strategies import NuggetV2
from src.strategies import NuggetV4
from src.strategies import NuggetV5
from src.strategies import SandboxV1
from src.strategies import SisterV1


class Mode(Enum):
    AUTOMATION = 'AUTOMATION'
    OPTIMIZATION = 'OPTIMIZATION'
    TESTING = 'TESTING'


class Exchange(Enum):
    BINANCE = 'BINANCE'
    BYBIT = 'BYBIT'


class Market(Enum):
    FUTURES = 'FUTURES'
    SPOT = 'SPOT'


class Strategy(Enum):
    DAILY_PROFIT_V1 = DailyProfitV1
    DEVOURER_V3 = DevourerV3
    MEAN_STRIKE_V1 = MeanStrikeV1
    NUGGET_V2 = NuggetV2
    NUGGET_V4 = NuggetV4
    NUGGET_V5 = NuggetV5
    SANDBOX_V1 = SandboxV1
    SISTER_V1 = SisterV1