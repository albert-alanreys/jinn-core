import json
import os
import re
from glob import glob
from logging import getLogger

import src.core.enums as enums
from src.services.automation.api_clients.telegram import TelegramClient
from src.services.testing.tester import Tester
from .realtime_provider import RealtimeProvider
from .api_clients.binance import BinanceClient
from .api_clients.bybit import BybitClient


class AutomationBuilder():
    def __init__(self, config: dict) -> None:
        self.exchange = config['exchange']
        self.symbol = config['symbol']
        self.interval = config['interval']
        self.strategy = config['strategy']

        self.realtime_provider = RealtimeProvider()
        self.telegram_client = TelegramClient()
        self.binance_client = BinanceClient(self.telegram_client)
        self.bybit_client = BybitClient(self.telegram_client)

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        strategy_contexts = {}

        for strategy in enums.Strategy:
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
                    case enums.Exchange.BINANCE.name:
                        client = self.binance_client
                    case enums.Exchange.BYBIT.name:
                        client = self.bybit_client

                try:
                    instance = strategy.value(client, **params)
                    market_data = self.realtime_provider.fetch_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        feeds=instance.params.get('feeds')
                    )
                    instance.start(market_data)
                    stats = Tester.test(instance)

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
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            try:
                instance = self.strategy.value(client)
                market_data = self.realtime_provider.fetch_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.interval,
                    feeds=instance.params.get('feeds')
                )
                instance.start(market_data)
                stats = Tester.test(instance)

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