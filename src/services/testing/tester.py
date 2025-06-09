import json
import os
import warnings
from glob import glob
from logging import getLogger
from re import match

import src.core.enums as enums
from src.core.storage.history_provider import HistoryProvider
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient
from src.services.automation.api_clients.telegram import TelegramClient
from .performance_metrics import get_performance_metrics


class Tester:
    def __init__(self, testing_config: dict) -> None:
        self.exchange = testing_config['exchange']
        self.market = testing_config['market']
        self.symbol = testing_config['symbol']
        self.interval = testing_config['interval']
        self.start = testing_config['start']
        self.end = testing_config['end']
        self.strategy = testing_config['strategy']

        self.history_provider = HistoryProvider()
        self.telegram_client = TelegramClient()
        self.binance_client = BinanceClient(self.telegram_client)
        self.bybit_client = BybitClient(self.telegram_client)

        self.strategy_contexts = {}

        self.logger = getLogger(__name__)

    def run(self) -> None:
        self.logger.info('Testing process started')

        for strategy in enums.Strategy:
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
                groups = match(pattern, basename).groups()
                exchange, market, symbol, interval = (
                    groups[0].upper(),
                    groups[1].upper(),
                    groups[2].upper(),
                    groups[3]
                )

                match exchange:
                    case enums.Exchange.BINANCE.name:
                        client = self.binance_client
                    case enums.Exchange.BYBIT.name:
                        client = self.bybit_client

                match market:
                    case enums.Market.FUTURES.name:
                        market = enums.Market.FUTURES
                    case enums.Market.SPOT.name:
                        market = enums.Market.SPOT

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
                        strategy_instance = strategy.value(
                            client=client,
                            opt_params=params['params'].values()
                        )
                        feeds = strategy_instance.params.get('feeds')
                        market_data = self.history_provider.fetch_data(
                            client=client,
                            market=market,
                            symbol=symbol,
                            interval=interval,
                            start=params['period']['start'],
                            end=params['period']['end'],
                            feeds=feeds
                        )

                        strategy_context = {
                            'name': strategy.name,
                            'type': strategy.value,
                            'instance': strategy_instance,
                            'client': client,
                            'market_data': market_data
                        }

                        equity, metrics = (
                            self.calculate_strategy(strategy_context)
                        )
                        strategy_context['equity'] = equity
                        strategy_context['metrics'] = metrics
                        context_id = str(id(strategy_context))
                        self.strategy_contexts[context_id] = strategy_context
                    except Exception:
                        self.logger.exception('An error occurred')

        if not self.strategy_contexts:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            try:
                strategy_instance = self.strategy.value(client)
                feeds = strategy_instance.params.get('feeds')
                market_data = self.history_provider.fetch_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.interval,
                    start=self.start,
                    end=self.end,
                    feeds=feeds
                )

                strategy_context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': strategy_instance,
                    'client': client,
                    'market_data': market_data
                }

                equity, metrics = self.calculate_strategy(strategy_context)
                strategy_context['equity'] = equity
                strategy_context['metrics'] = metrics
                context_id = str(id(strategy_context))
                self.strategy_contexts[context_id] = strategy_context
            except Exception:
                self.logger.exception('An error occurred')

    def calculate_strategy(self, strategy_context: dict) -> tuple:
        strategy_context['instance'].start(strategy_context['market_data'])

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=RuntimeWarning)
            equity, metrics = get_performance_metrics(
                strategy_context['instance'].params['initial_capital'],
                strategy_context['instance'].completed_deals_log
            )

        return equity, metrics