import json
import os
import re
from glob import glob
from logging import getLogger

from src.core.enums import Exchange, Strategy
from src.features.backtesting import BacktestingService
from src.infrastructure.providers import RealtimeProvider
from src.infrastructure.clients.exchanges.binance import BinanceClient
from src.infrastructure.clients.exchanges.bybit import BybitClient


class AutomationBuilder():
    """
    Builds automation contexts for trading strategies.

    Handles the creation of strategy contexts by loading configuration files,
    fetching real-time market data, and preparing strategy instances
    for automated trading.

    Args:
        config (dict): Configuration dictionary containing:
            - exchange: Exchange name (e.g., BINANCE, BYBIT)
            - symbol: Trading symbol (e.g., BTCUSDT)
            - interval: Time interval for data (e.g., '1h')
            - strategy: Trading strategy to automate
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize AutomationBuilder with configuration parameters.

        Sets up instance variables from configuration dictionary
        and initializes realtime provider, Binance client,
        Bybit client, and logger.

        Args:
            config (dict): Configuration dictionary containing exchange,
                           symbol, interval, and strategy parameters
        """

        self.exchange = config['exchange']
        self.symbol = config['symbol']
        self.interval = config['interval']
        self.strategy = config['strategy']

        self.realtime_provider = RealtimeProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        """
        Construct automation contexts for all strategies.

        Loads automation configurations from JSON files,
        fetches real-time market data, creates strategy instances,
        and runs backtests. Falls back to instance config if no
        strategy files are found.

        Returns:
            dict: Dictionary of strategy contexts keyed by context ID,
                  each containing:
                    - name: Strategy name
                    - type: Strategy type
                    - instance: Strategy instance
                    - client: Exchange API client
                    - market_data: Current market data
                    - stats: Backtesting statistics
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

                pattern1 = r'^([^_]+)_([^_]+)_([^_]+)\.json$'
                pattern2 = r'^([^_]+)_([^_]+)_([^_]+)_([^_]+)\.json$'

                match1 = re.fullmatch(pattern1, basename)
                match2 = re.fullmatch(pattern2, basename)

                if match1:
                    exchange, symbol, interval = (
                        match1.group(1).upper(),
                        match1.group(2).upper(),
                        match1.group(3)
                    )

                    with open(file_path, 'r') as file:
                        content = file.read()
                        content = (
                            content
                            .replace('True', 'true')
                            .replace('False', 'false')
                        )

                        try:
                            params = {
                                'all_params': json.loads(content)
                            }
                        except json.JSONDecodeError:
                            self.logger.error(
                                f'Failed to load JSON from {file_path}'
                            )
                            continue
                elif match2:
                    exchange, _, symbol, interval = (
                        match2.group(1).upper(),
                        match2.group(2),
                        match2.group(3).upper(),
                        match2.group(4)
                    )

                    with open(file_path, 'r') as file:
                        try:
                            params = {
                                'opt_params': json.load(file)[0]['params']
                            }
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
                    instance = strategy.value(client, **params)
                    market_data = self.realtime_provider.fetch_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        feeds=instance.params.get('feeds')
                    )
                    instance.calculate(market_data)
                    stats = BacktestingService.test(instance)

                    context = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': instance,
                        'client': client,
                        'market_data': market_data,
                        'stats': stats,
                        'updated': False,
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
                market_data = self.realtime_provider.fetch_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.interval,
                    feeds=instance.params.get('feeds')
                )
                instance.calculate(market_data)
                stats = BacktestingService.test(instance)

                context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'client': client,
                    'market_data': market_data,
                    'stats': stats,
                    'updated': False,
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts