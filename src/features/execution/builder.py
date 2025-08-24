from __future__ import annotations
from ast import literal_eval
from logging import getLogger
from typing import Any, TYPE_CHECKING

from src.core.providers import HistoryProvider, RealtimeProvider
from src.core.strategies import strategies
from src.infrastructure.exchanges import BinanceClient, BybitClient
from src.infrastructure.exchanges.models import Exchange, Interval

from .models import ContextConfig, StrategyContext
from .tester import StrategyTester

if TYPE_CHECKING:
    from src.core.providers.models import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient
    from .models import StrategyMetrics


logger = getLogger(__name__)


class ExecutionContextBuilder:
    """
    Builds complete execution contexts for trading strategies.
    
    Handles initialization of strategy instances, market data providers,
    exchange clients, and performance metrics calculation.
    """
    
    def __init__(self) -> None:
        """Initialize the context builder with required dependencies."""

        self._history_provider = HistoryProvider()
        self._realtime_provider = RealtimeProvider()
        self._binance_client = BinanceClient()
        self._bybit_client = BybitClient()
        self._strategy_tester = StrategyTester()
        
        self._exchange_clients: dict[str, BaseExchangeClient] = {
            Exchange.BINANCE.value: self._binance_client,
            Exchange.BYBIT.value: self._bybit_client,
        }
    
    def create(self, config: ContextConfig) -> StrategyContext:
        """
        Create a complete strategy context from configuration.
        
        Args:
            config: Strategy configuration containing all required parameters
            
        Returns:
            StrategyContext: Complete strategy context
        """

        strategy = self._create_strategy(config)
        client = self._get_exchange_client(config['exchange'])
        market_data = self._prepare_market_data(config, strategy, client)
        metrics = self._calculate_strategy_metrics(strategy)

        return {
            'name': config['strategy'],
            'strategy': strategy,
            'client': client,
            'market_data': market_data,
            'metrics': metrics,
            'is_live': config['is_live'],
        }
    
    def update(
        self,
        context: StrategyContext,
        param_name: str,
        param_value: Any
    ) -> StrategyContext:
        """
        Update parameter in strategy context and restart strategy.

        Args:
            context: Complete strategy execution context
            param_name: strategy parameter name
            param_value: new parameter value
            
        Returns:
            StrategyContext: Complete strategy context
        """

        def _parse_value(raw):
            if isinstance(raw, list):
                return [float(x) for x in raw]

            if isinstance(raw, str):
                try:
                    return literal_eval(raw.capitalize())
                except (ValueError, SyntaxError):
                    return raw.capitalize()

            return raw

        strategy = context['strategy']
        params = strategy.params

        old_value = params[param_name]
        new_value = _parse_value(param_value)

        if (
            isinstance(old_value, (int, float)) and
            isinstance(new_value, (int, float))
        ):
            new_value = type(old_value)(new_value)
        elif type(old_value) != type(new_value):
            raise TypeError()
        
        params[param_name] = new_value

        strategy_class = strategies[context['name']]
        strategy = strategy_class(params)
        metrics = self._calculate_strategy_metrics(
            strategy, context['market_data']
        )

        return {
            **context,
            'strategy': strategy,
            'metrics': metrics,
        }
    
    def _create_strategy(self, config: ContextConfig) -> BaseStrategy:
        """
        Create and initialize strategy instance from configuration.
        
        Args:
            config: Complete strategy configuration dictionary
            
        Returns:
            BaseStrategy:
                Initialized strategy instance with configured parameters
            
        Raises:
            ValueError: If strategy name is not found in registered strategies
        """

        strategy_name = config['strategy']
        
        if strategy_name not in strategies:
            raise ValueError(f'Unknown strategy: {strategy_name}')
        
        strategy_class = strategies[strategy_name]
        return strategy_class(config['params'])
    
    def _get_exchange_client(self, exchange: str) -> BaseExchangeClient:
        """
        Get the appropriate exchange client for the given exchange.
        
        Args:
            exchange: Exchange name as string
            
        Returns:
            BaseExchangeClient: Initialized exchange client instance
            
        Raises:
            ValueError: If the specified exchange is not supported
        """

        if exchange not in self._exchange_clients:
            raise ValueError(f'Unsupported exchange: {exchange}')
        
        return self._exchange_clients[exchange]
    
    def _prepare_market_data(
        self,
        config: ContextConfig,
        strategy: BaseStrategy,
        client: BaseExchangeClient,
    ) -> MarketData:
        """
        Prepare market data based on execution mode.
        
        Args:
            config: Strategy configuration containing data parameters
            strategy: Initialized strategy instance
            client: Exchange client instance for data retrieval
        
        Returns:
            MarketData: Market data package matching MarketData structure
        """

        common_params = {
            'client': client,
            'symbol': config['symbol'],
            'interval': Interval(config['interval']),
            'feeds': strategy.params.get('feeds'),
        }
        
        if config['is_live']:
            return self._realtime_provider.get_market_data(**common_params)
        else:
            return self._history_provider.get_market_data(
                start=config['start'],
                end=config['end'],
                **common_params
            )
    
    def _calculate_strategy_metrics(
        self,
        strategy: BaseStrategy,
        market_data: MarketData,
    ) -> StrategyMetrics:
        """
        Calculate initial performance metrics for the strategy.
        
        Args:
            strategy: Initialized strategy instance to test
            MarketData: Market data package matching MarketData structure
            
        Returns:
            Complete set of strategy performance metrics
        """

        strategy.calculate(market_data)
        return self._strategy_tester.test(strategy)