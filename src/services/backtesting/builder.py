import json
import os
import re
from glob import glob
from logging import getLogger

from src.core.enums import Exchange, Market, Strategy
from src.core.storage.history_provider import HistoryProvider
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient
from .backtester import Backtester


class BacktestingBuilder:
    def __init__(self, config: dict) -> None:
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
                        instance = strategy.value(
                            client=client,
                            opt_params=params['params'].values()
                        )
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
                        stats = Backtester.test(instance)

                        context = {
                            'name': strategy.name,
                            'type': strategy.value,
                            'instance': instance,
                            'client': client,
                            'market_data': market_data,
                            'stats': stats,
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
                stats = Backtester.test(instance)

                context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'client': client,
                    'market_data': market_data,
                    'stats': stats,
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts