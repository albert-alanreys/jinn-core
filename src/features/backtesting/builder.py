import json
import os
import re
from glob import glob
from logging import getLogger

from src.core.enums import Exchange, Market, Strategy
from src.infrastructure.clients.exchanges.binance import BinanceClient
from src.infrastructure.clients.exchanges.bybit import BybitClient
from src.infrastructure.providers import HistoryProvider
from .service import BacktestingService


class BacktestingBuilder:
    """
    Builds backtesting contexts for trading strategies.

    Handles the creation of strategy contexts by loading configuration files,
    fetching historical market data, and preparing strategy instances
    for backtesting.

    Args:
        config (dict): Configuration dictionary containing:
            - exchange: Exchange name (e.g., BINANCE, BYBIT)
            - market: Market type (e.g., FUTURES, SPOT)
            - symbol: Trading symbol (e.g., BTCUSDT)
            - interval: Time interval for data (e.g., '1h')
            - start: Start date for data (format: 'YYYY-MM-DD')
            - end: End date for data (format: 'YYYY-MM-DD')
            - strategy: Trading strategy to backtest
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize BacktestingBuilder with configuration parameters.

        Sets up instance variables from configuration dictionary
        and initializes history provider, Binance client,
        Bybit client, and logger.

        Args:
            config (dict): Configuration dictionary containing exchange,
                           market, symbol, interval, start, end,
                           and strategy parameters
        """

        self.exchange = config['exchange']
        self.market = config['market']
        self.symbol = config['symbol']
        self.interval = config['interval']
        self.start = config['start']
        self.end = config['end']
        self.strategy = config['strategy']

        self.history_provider = HistoryProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        """
        Construct backtesting contexts for all strategies.

        Loads backtesting configurations from JSON files,
        fetches historical market data, creates strategy instances,
        and runs backtests. Falls back to instance config if no
        strategy files are found.

        Returns:
            dict: Dictionary of strategy contexts keyed by context ID,
                  each containing:
                    - name: Strategy name
                    - type: Strategy type
                    - instance: Strategy instance
                    - client: Exchange API client
                    - market_data: Historical market data
                    - metrics: Strategy metrics from backtesting
        """

        strategy_contexts = {}

        for strategy in Strategy:
            folder_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'backtesting'
                )
            )
            file_paths = glob(f'{folder_path}/*.json')

            for file_path in file_paths:
                basename = os.path.basename(file_path) 
                pattern = r'(\w+)_(\w+)_(\w+)_(\w+)\.json'
                groups = re.match(pattern, basename).groups()
                exchange, market, symbol, interval = (
                    groups[0].upper(),
                    groups[1].upper(),
                    groups[2].upper(),
                    groups[3]
                )

                match exchange:
                    case Exchange.BINANCE.name:
                        client = self.binance_client
                    case Exchange.BYBIT.name:
                        client = self.bybit_client

                match market:
                    case Market.FUTURES.name:
                        market = Market.FUTURES
                    case Market.SPOT.name:
                        market = Market.SPOT

                with open(file_path, 'r') as file:
                    try:
                        params_dicts = json.load(file)
                    except json.JSONDecodeError:
                        self.logger.error(
                            f'Failed to load JSON from {file_path}'
                        )
                        continue

                for params in params_dicts:
                    try:
                        instance = strategy.value(client, params['params'])
                        market_data = self.history_provider.fetch_data(
                            client=client,
                            market=market,
                            symbol=symbol,
                            interval=interval,
                            start=params['period']['start'],
                            end=params['period']['end'],
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
                            'metrics': metrics,
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
                market_data = self.history_provider.fetch_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.interval,
                    start=self.start,
                    end=self.end,
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
                    'metrics': metrics,
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts