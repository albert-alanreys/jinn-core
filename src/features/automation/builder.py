import json
import os
import re
from glob import glob
from logging import getLogger

from src.core.enums import Exchange, Strategy
from src.features.backtesting import BacktestingService
from src.infrastructure.providers import RealtimeProvider
from src.infrastructure.clients.exchanges import BinanceClient
from src.infrastructure.clients.exchanges import BybitClient


class AutomationBuilder():
    """
    Builds automation contexts for trading strategies.

    Handles the creation of strategy contexts by loading configuration files,
    fetching real-time market data, and preparing strategy instances
    for automated trading.
    """

    def __init__(self, settings: dict) -> None:
        """
        Initialize AutomationBuilder with configuration parameters.

        Sets up instance variables from configuration dictionary
        and initializes realtime provider, Binance client,
        Bybit client, and logger.

        Args:
            settings (dict): Configuration dictionary containing:
                - exchange: Exchange name
                - symbol (str): Trading symbol
                - interval: Kline interval
                - strategy: Trading strategy to automate
        """

        self.exchange = settings['exchange']
        self.symbol = settings['symbol']
        self.interval = settings['interval']
        self.strategy = settings['strategy']

        self.realtime_provider = RealtimeProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        """
        Construct automation contexts for all strategies.

        Loads automation configurations from JSON files,
        fetches real-time market data, creates strategy instances,
        and runs backtests. Falls back to instance settings if no
        strategy files are found.

        Returns:
            dict: Dictionary of strategy contexts keyed by context ID,
                  each containing:
                    - name: Strategy name
                    - type: Strategy type
                    - instance: Strategy instance
                    - client: Exchange API client
                    - market_data: Current market data
                    - metrics: Strategy metrics from backtesting
                    - updated: Flag indicating if context was updated
        """

        strategy_contexts = {}

        for strategy in Strategy:
            folder_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'automation'
                )
            )
            file_paths = glob(f'{folder_path}/*.json')

            for file_path in file_paths:
                basename = os.path.basename(file_path)
                pattern = r'(\w+)_(\w+)_(\w+)\.json'
                groups = re.match(pattern, basename).groups()
                exchange, symbol, interval = (
                    groups[0].upper(),
                    groups[1].upper(),
                    groups[2]
                )

                with open(file_path, 'r') as file:
                    content = file.read()
                    content = (
                        content
                        .replace('True', 'true')
                        .replace('False', 'false')
                    )

                try:
                    json_data = json.loads(content)
                    
                    if isinstance(json_data, list):
                        if json_data and 'params' in json_data[0]:
                            params = {'params': json_data[0]['params']}
                        else:
                            self.logger.error(
                                f'Invalid array format in {file_path}'
                            )
                            continue
                    else:
                        params = {'params': json_data}
                        
                except json.JSONDecodeError:
                    self.logger.error(
                        f'Failed to load JSON from {file_path}'
                    )
                    continue

                match exchange:
                    case Exchange.BINANCE.name:
                        client = self.binance_client
                    case Exchange.BYBIT.name:
                        client = self.bybit_client

                try:
                    print(params)

                    instance = strategy.value(client, **params)
                    market_data = self.realtime_provider.get_market_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        feeds=instance.params.get('feeds')
                    )
                    instance.calculate(market_data)
                    metrics = BacktestingService.test(instance)

                    context = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': instance,
                        'client': client,
                        'market_data': market_data,
                        'metrics': metrics
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
                instance = self.strategy.value(client)
                market_data = self.realtime_provider.get_market_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.interval,
                    feeds=instance.params.get('feeds')
                )
                instance.calculate(market_data)
                metrics = BacktestingService.test(instance)

                context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'client': client,
                    'market_data': market_data,
                    'metrics': metrics
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts