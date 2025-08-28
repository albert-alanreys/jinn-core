from __future__ import annotations
from logging import getLogger
from typing import TYPE_CHECKING

from src.core.providers import HistoryProvider
from src.core.strategies import strategies
from src.infrastructure.exchanges import BinanceClient, BybitClient
from src.infrastructure.exchanges.models import Exchange, Interval

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from src.infrastructure.exchanges import BaseExchangeClient
    from .models import ContextConfig, StrategyContext


logger = getLogger(__name__)


class OptimizationContextBuilder:
    """
    Builds optimization contexts for trading strategies.
    
    This class manages initialization of:
      - Strategy instances
      - Market data providers
      - Exchange clients
    """
    
    def __init__(self) -> None:
        """Initialize the builder with required dependencies."""

        self._history_provider = HistoryProvider()
        self._binance_client = BinanceClient()
        self._bybit_client = BybitClient()
        
        self._exchange_clients: dict[str, BaseExchangeClient] = {
            Exchange.BINANCE.value: self._binance_client,
            Exchange.BYBIT.value: self._bybit_client,
        }
    
    def create(self, config: ContextConfig) -> StrategyContext:
        """
        Build a strategy optimization context from configuration.
        
        Args:
            config: Context configuration package
        
        Returns:
            StrategyContext: Initialized strategy context
        """

        strategy_class = self._get_strategy_class(config['strategy'])
        client = self._get_exchange_client(config['exchange'])
        market_data = self._get_market_data(config, strategy_class, client)

        return {
            'name': config['strategy'],
            'exchange': config['exchange'],
            'market_data': market_data,
            'strategy_class': strategy_class,
            'optimized_params': None,
        }
   
    def _get_strategy_class(self, strategy: str) -> type[BaseStrategy]:
        """
        Get the strategy class from registry.

        Args:
            strategy: Strategy name

        Returns:
            type[BaseStrategy]: Strategy class

        Raises:
            ValueError: If the strategy name is not found in the registry
        """
        
        if strategy not in strategies:
            raise ValueError(f'Unknown strategy: {strategy}')
        
        return strategies[strategy]
    
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
        strategy_class: type[BaseStrategy],
        client: BaseExchangeClient,
    ) -> MarketData:
        """
        Get historical data market data.
        
        Args:
            config: Context configuration package
            strategy_class: Strategy class
            client: Exchange client for data retrieval
        
        Returns:
            MarketData: Market data package
        """

        return self._history_provider.get_market_data(
            client=client,
            symbol=config['symbol'],
            interval=Interval(config['interval']),
            start=config['start'],
            end=config['end'],
            feeds=strategy_class.feeds
        )