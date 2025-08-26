from __future__ import annotations
from ast import literal_eval
from logging import getLogger
from typing import Any, TYPE_CHECKING

from src.core.providers import HistoryProvider, RealtimeProvider
from src.core.strategies import strategies
from src.infrastructure.exchanges import BinanceClient, BybitClient
from src.infrastructure.exchanges.models import Exchange, Interval
from .tester import StrategyTester

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient
    from .models import ContextConfig, StrategyContext


logger = getLogger(__name__)


class ExecutionContextBuilder:
    """
    Builds execution contexts for trading strategies.
    
    This class manages initialization of:
      - Strategy instances
      - Market data providers
      - Exchange clients
      - Performance metrics calculation
    """
    
    def __init__(self) -> None:
        """Initialize the builder with required dependencies."""

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
        Build a complete strategy execution context from configuration.
        
        Args:
            config: Context configuration package
            
        Returns:
            StrategyContext: Initialized strategy context
        """

        strategy = self._create_strategy(config)
        client = self._get_exchange_client(config['exchange'])
        market_data = self._get_market_data(config, strategy, client)
        metrics = self._strategy_tester.test(strategy, market_data)

        return {
            'name': config['strategy'],
            'is_live': config['is_live'],
            'strategy': strategy,
            'client': client,
            'market_data': market_data,
            'metrics': metrics,
        }
    
    def update(
        self,
        context: StrategyContext,
        param_name: str,
        param_value: Any
    ) -> StrategyContext:
        """
        Update a strategy parameter and rebuild its execution context.

        Args:
            context: Existing strategy context package
            parameter_name: Name of the parameter to update
            parameter_value: New parameter value

        Returns:
            StrategyContext:
                Updated strategy context with recalculated metrics

        Raises:
            TypeError: If parameter type does not match existing one
        """

        strategy = context['strategy']
        params = strategy.params

        old_value = params[param_name]
        new_value = self._normalize_parameter_value(param_value)

        if (
            isinstance(old_value, (int, float)) and
            isinstance(new_value, (int, float))
        ):
            new_value = type(old_value)(new_value)
        elif type(old_value) != type(new_value):
            raise TypeError(
                f'Type mismatch for parameter {param_name}: '
                f'{type(old_value).__name__} vs {type(new_value).__name__}'
            )

        params[param_name] = new_value
        strategy = self._create_strategy(
            {'strategy': context['name'], 'params': params}
        )
        metrics = self._strategy_tester.test(strategy, context['market_data'])

        return {
            **context,
            'strategy': strategy,
            'metrics': metrics,
        }
    
    def _create_strategy(self, config: ContextConfig) -> BaseStrategy:
        """
        Create a strategy instance from the name specified in configuration.

        Args:
            config: Context configuration package

        Returns:
            BaseStrategy: Initialized strategy instance

        Raises:
            ValueError: If the strategy name is not found in the registry
        """

        strategy_name = config['strategy']
        
        if strategy_name not in strategies:
            raise ValueError(f'Unknown strategy: {strategy_name}')
        
        strategy_class = strategies[strategy_name]
        return strategy_class(config['params'])
    
    def _get_exchange_client(self, exchange: str) -> BaseExchangeClient:
        """
        Get the client for the given exchange name.
        
        Args:
            exchange: Exchange name
            
        Returns:
            BaseExchangeClient: Exchange client instance
            
        Raises:
            ValueError: If the exchange is not supported
        """

        if exchange not in self._exchange_clients:
            raise ValueError(f'Unsupported exchange: {exchange}')
        
        return self._exchange_clients[exchange]
    
    def _get_market_data(
        self,
        config: ContextConfig,
        strategy: BaseStrategy,
        client: BaseExchangeClient,
    ) -> MarketData:
        """
        Get market data from appropriate provider based on execution mode.

        Returns real-time data for live mode or
        historical data for backtest mode.
        
        Args:
            config: Context configuration package
            strategy: Initialized strategy instance
            client: Exchange client for data retrieval
        
        Returns:
            MarketData: Market data package
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
    
    @staticmethod
    def _normalize_parameter_value(raw: Any) -> Any:
        """Normalize raw parameter input into the correct Python type."""

        if isinstance(raw, list):
            return [float(x) for x in raw]

        if isinstance(raw, str):
            try:
                return literal_eval(raw.capitalize())
            except (ValueError, SyntaxError):
                return raw.capitalize()

        return raw