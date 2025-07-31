from enum import Enum

from src.strategies import DailyProfitV1
from src.strategies import DevourerV3
from src.strategies import MeanStrikeV1
from src.strategies import MeanStrikeV2
from src.strategies import NuggetV2
from src.strategies import NuggetV4
from src.strategies import NuggetV5
from src.strategies import SandboxV1
from src.strategies import SisterV1


class Mode(Enum):
    """
    Application operating modes.
    
    Defines the available modes for running the Jinn trading application:
    - OPTIMIZATION: Parameter optimization using genetic algorithms
    - BACKTESTING: Strategy performance testing on historical data
    - AUTOMATION: Live trading automation with real-time execution
    """

    OPTIMIZATION = 'OPTIMIZATION'
    BACKTESTING = 'BACKTESTING'
    AUTOMATION = 'AUTOMATION'


class Exchange(Enum):
    """
    Supported cryptocurrency exchanges.
    
    Defines the available exchanges for trading operations:
    - BINANCE: Binance exchange integration
    - BYBIT: Bybit exchange integration
    """

    BINANCE = 'BINANCE'
    BYBIT = 'BYBIT'


class Market(Enum):
    """
    Trading market types.
    
    Defines the available market types for trading:
    - FUTURES: Futures/derivatives trading
    - SPOT: Spot trading (immediate settlement)
    """

    FUTURES = 'FUTURES'
    SPOT = 'SPOT'


class Strategy(Enum):
    """
    Available strategies. Maps strategy names
    to their corresponding implementation classes.
    """

    DAILY_PROFIT_V1 = DailyProfitV1
    DEVOURER_V3 = DevourerV3
    MEAN_STRIKE_V1 = MeanStrikeV1
    MEAN_STRIKE_V2 = MeanStrikeV2
    NUGGET_V2 = NuggetV2
    NUGGET_V4 = NuggetV4
    NUGGET_V5 = NuggetV5
    SANDBOX_V1 = SandboxV1
    SISTER_V1 = SisterV1