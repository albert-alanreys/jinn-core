from __future__ import annotations
from logging import getLogger
from os import getenv
from typing import TYPE_CHECKING

from src.core.providers import HistoryProvider, RealtimeProvider
from src.core.strategies import strategy_registry
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
        self._strategy_tester = StrategyTester()
        
        self._exchange_clients: dict[str, BaseExchangeClient] = {
            Exchange.BINANCE.value: BinanceClient,
            Exchange.BYBIT.value: BybitClient,
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
        clients = self._get_exchange_clients(config['exchange'])
        market_data = self._get_market_data(config, strategy, clients[0])
        metrics = self._strategy_tester.test(strategy, market_data)

        return {
            'name': config['strategy'],
            'exchange': config['exchange'],
            'is_live': self._is_live(config),
            'strategy': strategy,
            'clients': clients,
            'market_data': market_data,
            'metrics': metrics,
        }
    
    def update(
        self,
        context: StrategyContext,
        param_name: str,
        param_value: bool | int | float
    ) -> StrategyContext:
        """
        Update a strategy parameter and rebuild execution context.

        Args:
            context: Strategy context package
            parameter_name: Name of the parameter to update
            parameter_value: New parameter value

        Returns:
            StrategyContext:
                Updated strategy context with recalculated metrics
        """

        strategy = context['strategy']
        params = strategy.params.copy()

        old_value = params[param_name]
        params[param_name] = type(old_value)(param_value)

        strategy = self._create_strategy({
            'strategy': context['name'], 
            'params': params
        })
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
        
        if strategy_name not in strategy_registry:
            raise ValueError(f'Unknown strategy: {strategy_name}')
        
        strategy_class = strategy_registry[strategy_name]
        return strategy_class(config['params'])
    
    def _get_exchange_clients(self, exchange: str) -> list[BaseExchangeClient]:
        """
        Get multiple client instances for the given exchange name.
        
        If no API keys are configured, returns a single client
        with empty credentials for market data access only.
        
        Args:
            exchange: Exchange name to get clients for
                
        Returns:
            list[BaseExchangeClient]: List of exchange client instances
            (returns one empty client if no credentials provided)
                
        Raises:
            ValueError: If the exchange is not supported
        """
        
        if exchange not in self._exchange_clients:
            raise ValueError(f'Unsupported exchange: {exchange}')
        
        api_keys_str = getenv(f'{exchange.upper()}_API_KEYS', '')
        api_secrets_str = getenv(f'{exchange.upper()}_API_SECRETS', '')
        
        api_keys = [
            k.strip() for k in api_keys_str.split(',') if k.strip()
        ]
        api_secrets = [
            s.strip() for s in api_secrets_str.split(',') if s.strip()
        ]
        
        if not api_keys and not api_secrets:
            client_class = self._exchange_clients[exchange]
            return [client_class()]
        
        if len(api_keys) != len(api_secrets):
            raise ValueError(
                f'Mismatch in number of API keys and secrets for {exchange}: '
                f'{len(api_keys)} keys vs {len(api_secrets)} secrets'
            )
        
        client_class = self._exchange_clients[exchange]
        return [client_class(k, s) for k, s in zip(api_keys, api_secrets)]
    
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
            'feeds': strategy.feeds,
        }
        
        if self._is_live(config):
            return self._realtime_provider.get_market_data(**common_params)
        else:
            return self._history_provider.get_market_data(
                start=config['start'],
                end=config['end'],
                **common_params
            )
    
    def _is_live(self, config: ContextConfig) -> bool:
        """
        Determine execution mode from configuration.

        Returns True when no backtest boundaries are defined.
        Returns False when 'start' or 'end' fields are present,
        indicating backtest execution.
        
        Args:
            config: Strategy context configuration package

        Returns:
            bool: Execution mode flag (True for live, False for backtest)
        """

        return not (config.get('start') or config.get('end'))