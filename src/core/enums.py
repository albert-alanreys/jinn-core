from enum import Enum

from src.core.strategies import DailyProfitV1
from src.core.strategies import DevourerV3
from src.core.strategies import MeanStrikeV1
from src.core.strategies import MeanStrikeV2
from src.core.strategies import NuggetV2
from src.core.strategies import NuggetV4
from src.core.strategies import NuggetV5
from src.core.strategies import ExampleV1
from src.core.strategies import ExampleV2
from src.core.strategies import SisterV1


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


class Strategy(Enum):
    """
    Available strategies. Maps strategy names
    to their corresponding implementation classes.
    """

    DAILY_PROFIT_V1 = DailyProfitV1
    DEVOURER_V3 = DevourerV3
    EXAMPLE_V1 = ExampleV1
    EXAMPLE_V2 = ExampleV2
    MEAN_STRIKE_V1 = MeanStrikeV1
    MEAN_STRIKE_V2 = MeanStrikeV2
    NUGGET_V2 = NuggetV2
    NUGGET_V4 = NuggetV4
    NUGGET_V5 = NuggetV5
    SISTER_V1 = SisterV1