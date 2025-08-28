from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np

from .utils import order_cache

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    Provides common functionality for strategy initialization,
    parameter handling, and order caching. Concrete strategies
    must implement the calculate() and trade() methods.

    Common Parameters (inherited by all strategies):
        direction (int):            Trading direction 
                                    0=all, 1=longs, 2=shorts
                                    (default: 0)
        margin_type (int):          Margin mode 
                                    0=ISOLATED, 1=CROSSED
                                    (default: 0)
        leverage:             Leverage multiplier 
                                    (1 = no leverage)
                                    (default: 1)
        initial_capital (float):    Starting capital 
                                    in USDT
                                    (default: 10000.0)
        commission (float):         Trading fee 
                                    (0.05 = 0.05%)
                                    (default: 0.05)
        position_size_type (int):   Position size calculation mode 
                                    0=PERCENT, 1=USDT
                                    (default: 0)
        position_size (float):      Position size 
                                    (% or USDT based on position_size_type)
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

        indicators: Actual indicator values to render.
            Key: Indicator name (str)
            Value: dict with:
                - 'options': reference to indicator_options[name]
                - 'values': sequence of values
                - 'colors': optional sequence of point-specific colors
    """

    # Common trading default parameter values for all strategies
    base_params = {
        # Core trading settings
        'direction': 0,              # 0 - all, 1 - longs, 2 - shorts
        'margin_type': 0,            # 0 - ISOLATED, 1 - CROSSED
        'leverage': 1,               # Leverage multiplier
        
        # Capital management
        'initial_capital': 10000.0,  # Starting capital in USDT
        'position_size_type': 0,        # 0 - PERCENT, 1 - CURRENCY
        'position_size': 100.0,         # Size in % or absolute value
        'commission': 0.05,          # Fee percentage (0.05 = 0.05%)
    }

    # Default parameter values for backtesting and live trading
    params = {}

    # Market data sources required for strategy calculations
    feeds = {}

    # Parameter ranges for hyperparameter optimization
    opt_params = {}

    # Human-readable labels for frontend parameter display
    base_param_labels = {
        'direction': 'Trade Direction',
        'margin_type': 'Margin Type',
        'leverage': 'Leverage',
        'initial_capital': 'Initial Capital (USDT)',
        'position_size_type': 'Position Size Type',
        'position_size': 'Position Size',
        'commission': 'Commission (%)',
    }
    param_labels = {}

    # Chart styling configuration for technical indicators
    indicator_options = {}

    # Indicator Visualization Data
    indicators = {}

    def __init__(self, params: dict | None = None) -> None:
        """
        Initialize the trading strategy with a client and parameters.

        Args:
            params: Dictionary of parameters
        """

        self.params = {
            **self.base_params,
            **deepcopy(self.params)
        }

        if params is not None:
            self.params.update(params)
    
    @property
    def all_params(self) -> dict[str, bool | int | float]:
        """Return a copy of all strategy parameters."""

        return self.params.copy()
    
    @property
    def all_labels(self) -> dict[str, str]:
        """Return a copy of all strategy parameter labels."""

        return {**self.base_param_labels, **self.param_labels}

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
                - symbol: str - Trading symbol
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
        self.position_type = np.nan
        self.order_signal = np.nan
        self.order_price = np.nan
        self.order_date = np.nan
        self.order_size = np.nan

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

        # Additional market data
        self.feeds_data = {'klines': {}}

        if market_data['feeds']:
            for feed_name, feed_data in (
                market_data['feeds']['klines'].items()
            ):
                self.feeds_data['klines'][feed_name] = {
                    'time': feed_data[:, 0],
                    'open': feed_data[:, 1],
                    'high': feed_data[:, 2],
                    'low': feed_data[:, 3],
                    'close': feed_data[:, 4],
                    'volume': feed_data[:, 5]
                }

        # Strategy parameters
        self.equity = self.params['initial_capital']

    def trade(self, client: BaseExchangeClient) -> None:
        """
        Execute trading strategy with automatic order cache management.
        
        This method handles the complete trading workflow including:
        - Loading cached order IDs from database
        - Executing strategy-specific trading logic
        - Saving updated order IDs back to database
        
        The order cache is automatically managed using SQLite database
        with structure: {exchange_name}.db -> order_identifiers table.
        Cache key format: {strategy_name}_{symbol}
        
        Order cache contains:
        - stop_ids: List of active stop order identifiers
        - limit_ids: List of active limit order identifiers
        
        Args:
            client: Exchange client instance
        """

        if not hasattr(self, 'order_ids'):
            self.order_ids = order_cache.load_order_cache(
                strategy=self.__class__.__name__,
                exchange=client.exchange_name,
                symbol=self.symbol
            )

        try:
            self._trade(client)
        finally:
            order_cache.save_order_cache(
                strategy=self.__class__.__name__,
                exchange=client.exchange_name,
                symbol=self.symbol,
                order_ids=self.order_ids
            )

    @abstractmethod
    def calculate(self, market_data: dict) -> None:
        """
        Calculate strategy indicators and signals.  
        Must be implemented by concrete strategy classes.

        Args:
            market_data: Dictionary containing market data with structure:
                - symbol: str
                - klines: np.ndarray [time, open, high, low, close, volume]
                - extra_klines: dict
                - p_precision: float
                - q_precision: float
        """
        pass

    @abstractmethod
    def _trade(self, client: BaseExchangeClient) -> None:
        """
        Execute trading logic based on calculated signals.  
        Must be implemented by concrete strategy classes.
        """
        pass