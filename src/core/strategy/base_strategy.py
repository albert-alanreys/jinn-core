import os
from abc import ABC, abstractmethod
from copy import deepcopy
from inspect import getfile
from typing import TYPE_CHECKING

import numpy as np

from .order_cache import OrderCache

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceClient
    from src.services.automation.api_clients.bybit import BybitClient


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Provides common functionality for strategy initialization,
    parameter handling, and order caching. Concrete strategies
    must implement the calculate() and trade() methods.

    Common Parameters (inherited by all strategies):
        direction (int):         Trading direction 
                                 0=all, 1=longs, 2=shorts
                                 (default: 0)
        margin_type (int):       Margin mode 
                                 0=ISOLATED, 1=CROSSED
                                 (default: 0)
        leverage (int):          Leverage multiplier 
                                 (1 = no leverage)
                                 (default: 1)
        initial_capital (float): Starting capital 
                                 in USDT
                                 (default: 10000.0)
        commission (float):      Trading fee 
                                 (0.05 = 0.05%)
                                 (default: 0.05)
        order_size_type (int):   Size calculation mode 
                                 0=PERCENT, 1=USDT
                                 (default: 0)
        order_size (float):      Order size 
                                 (% or USDT based on order_size_type)
                                 (default: 100.0)

    Indicator Configuration (for frontend rendering):
        indicator_options (dict): Display settings for each indicator.
            Key: Indicator name (str)
            Value: dict with options:
                - 'pane': int — panel number (0 = main, 1+ = subpanels)
                - 'type': str — chart type ('line' or 'histogram')
                - 'lineWidth': int — optional line thickness
                - 'color': str — optional encoded color
                - 'lineStyle': int — optional line pattern. Allowed values:
                    0: solid
                    1: dotted
                    2: dashed
                    3: large dashed
                    4: sparse dotted
                - 'lineType': int — optional line shape. Allowed values:
                    0: Simple
                    1: WithSteps
                    2: Curved
                - 'lineVisible': bool — optional flag to control 
                                        line visibility

        indicators (dict): Actual indicator values to render.
            Key: Indicator name (str)
            Value: dict with:
                - 'options': reference to indicator_options[name]
                - 'values': sequence of values
                - 'colors': optional sequence of point-specific colors
    """

    # Common trading parameters for all strategies
    base_params = {
        # Core trading settings
        "direction": 0,              # 0 - all, 1 - longs, 2 - shorts
        "margin_type": 0,            # 0 - ISOLATED, 1 - CROSSED
        "leverage": 1,               # Leverage multiplier
        
        # Capital management
        "initial_capital": 10000.0,  # Starting capital in USDT
        "order_size_type": 0,        # 0 - PERCENT, 1 - CURRENCY
        "order_size": 100.0,         # Size in % or absolute value
        "commission": 0.05,          # Fee percentage (0.05 = 0.05%)
    }

    # Frontend rendering settings for indicators
    indicator_options = {}

    # Indicator values for visualization
    indicators = {}

    def __init__(
        self,
        client: 'BinanceClient | BybitClient',
        all_params: dict | None = None,
        opt_params: dict | list | None = None
    ) -> None:
        """
        Initialize the trading strategy with a client and parameters.

        Args:
            client: Exchange API client instance (Binance or Bybit).
            all_params: Dictionary of parameters to override defaults.
            opt_params: Parameters for optimization, either as a dict or list.
        """

        self.params = {
            **self.base_params,
            **deepcopy(self.params)
        }

        if all_params is not None:
            self.params.update(all_params)

        if opt_params is not None:
            if isinstance(opt_params, dict):
                self.params.update(opt_params)
            else:
                opt_param_keys = getattr(self, 'opt_params', [])
                for key, value in zip(opt_param_keys, opt_params):
                    self.params[key] = value

        self.client = client
        self.cache = OrderCache(
            base_dir=os.path.join(
                os.path.dirname(getfile(self.__class__)), '__cache__'
            ),
            exchange=self.client.EXCHANGE
        )
        self.order_ids = None

    def init_variables(
        self,
        market_data: dict,
        max_open_deals: int = 1
    ) -> None:
        """
        Initialize core strategy variables from market data.

        Sets up:
        - Deal logs (completed and open)
        - Position tracking variables
        - Market data references
        - Precision parameters
        - Equity tracking

        Args:
            market_data: Dictionary containing:
                - symbol: str - Trading pair symbol
                - p_precision: float - Price precision step
                - q_precision: float - Quantity precision step
                - klines: np.ndarray - OHLCV data with columns:
                    [time, open, high, low, close, volume]
                - feeds: dict - Additional data
            max_open_deals: Maximum number of simultaneously open deals.
                            Determines number of rows in open_deals_log.
                            Each deal will have exactly 5 tracking values.
        """

        # Deal logs
        self.completed_deals_log = np.empty((0, 13), dtype=np.float64)
        self.open_deals_log = np.full((max_open_deals, 5), np.nan)

        # Position tracking
        self.position_size = np.nan
        self.entry_signal = np.nan
        self.entry_price = np.nan
        self.entry_date = np.nan
        self.deal_type = np.nan

        # Market identity
        self.symbol = market_data['symbol']

        # Precision parameters
        self.p_precision = market_data['p_precision']
        self.q_precision = market_data['q_precision']

        # Core market data (klines)
        self.time = market_data['klines'][:, 0]
        self.open = market_data['klines'][:, 1]
        self.high = market_data['klines'][:, 2]
        self.low = market_data['klines'][:, 3]
        self.close = market_data['klines'][:, 4]
        self.volume = market_data['klines'][:, 5]

        # Supplementary feeds
        self.feeds = market_data['feeds']

        # Strategy parameters
        self.equity = self.params['initial_capital']

    @abstractmethod
    def calculate(self, market_data: dict) -> None:
        """
        Calculate strategy indicators and signals.

        Args:
            market_data: Dictionary containing market data with structure:
                - symbol: str
                - klines: np.ndarray [time, open, high, low, close, volume]
                - extra_klines: dict
                - p_precision: float
                - q_precision: float

        Note:
            Must be implemented by concrete strategy classes.
            Should update strategy state and generate signals.
        """
        pass

    @abstractmethod
    def trade(self) -> None:
        """
        Execute trading logic based on calculated signals.

        Note:
            Must be implemented by concrete strategy classes.
            Should interact with exchange client to place/cancel orders.
        """
        pass