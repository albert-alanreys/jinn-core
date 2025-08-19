import json
import os
from logging import getLogger

from src.core.enums import Exchange, Strategy
from src.core.providers import HistoryProvider
from src.infrastructure.exchanges import BinanceClient
from src.infrastructure.exchanges import BybitClient


class OptimizationBuilder:
    """
    Builds optimization contexts for trading strategies.

    Handles the creation of strategy contexts by loading configuration files,
    fetching market data, and preparing data splits for training and testing.
    """

    def __init__(self, settings: dict) -> None:
        """
        Initialize OptimizationBuilder with configuration parameters.

        Sets up instance variables from configuration dictionary
        and initializes history provider, Binance client,
        Bybit client, and logger.

        Args:
            settings (dict): Configuration dictionary containing:
                - strategy: Trading strategy to optimize
                - exchange: Exchange name
                - symbol (str): Trading symbol
                - interval: Kline interval
                - start: Start date for data (format: 'YYYY-MM-DD')
                - end: End date for data (format: 'YYYY-MM-DD')
        """

        self.strategy = settings['strategy']
        self.exchange = settings['exchange']
        self.symbol = settings['symbol']
        self.interval = settings['interval']
        self.start = settings['start']
        self.end = settings['end']

        self.history_provider = HistoryProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        """
        Construct optimization contexts for all strategies.

        Loads optimization configurations from JSON files,
        fetches market data, and creates contexts for each strategy.
        Falls back to instance settings if no strategy files are found.

        Returns:
            dict: Dictionary of strategy contexts keyed by context ID,
                  each containing:
                    - name: Strategy name
                    - type: Strategy type
                    - client (BaseExchangeClient): Exchange API client
                    - market_data: Training and test data
        """

        strategy_contexts = {}

        for strategy in Strategy:
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'optimization',
                    'optimization.json'
                )
            )

            if not os.path.exists(file_path):
                continue

            with open(file_path, 'r') as file:
                try:
                    configs = json.load(file)
                except json.JSONDecodeError:
                    self.logger.error(f'Failed to load JSON from {file_path}')
                    continue

            for config in configs:
                exchange = config['exchange'].upper()
                symbol = config['symbol'].upper()
                interval = config['interval']
                start = config['start']
                end = config['end']

                match exchange:
                    case Exchange.BINANCE.name:
                        client = self.binance_client
                    case Exchange.BYBIT.name:
                        client = self.bybit_client

                try:
                    market_data = self.history_provider.get_market_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        start=start,
                        end=end,
                        feeds=strategy.value.params.get('feeds')
                    )
                    context = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'client': client,
                        'market_data': market_data
                    }
                    strategy_contexts[str(id(context))] = context
                except Exception:
                    self.logger.exception('An error occurred')

        if not strategy_contexts:
            match self.exchange:
                case Exchange.BINANCE:
                    client = self.binance_client
                case Exchange.BYBIT:
                    client = self.bybit_client

            try:
                market_data = self.history_provider.get_market_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.interval,
                    start=self.start,
                    end=self.end,
                    feeds=self.strategy.value.params.get('feeds')
                )
                context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'client': client,
                    'market_data': market_data
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts