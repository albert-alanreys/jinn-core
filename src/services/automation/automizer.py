import json
import os
from glob import glob
from logging import getLogger
from re import fullmatch
from threading import Thread
from time import sleep

import src.core.enums as enums
from src.services.automation.api_clients.telegram import TelegramClient
from .realtime_provider import RealtimeProvider
from .api_clients.binance import BinanceClient
from .api_clients.bybit import BybitClient


class Automizer():
    def __init__(self, automation_config: dict) -> None:
        self.exchange = automation_config['exchange']
        self.symbol = automation_config['symbol']
        self.interval = automation_config['interval']
        self.strategy = automation_config['strategy']

        self.realtime_provider = RealtimeProvider()
        self.telegram_client = TelegramClient()
        self.binance_client = BinanceClient(self.telegram_client)
        self.bybit_client = BybitClient(self.telegram_client)

        self.strategy_contexts = {}
        self.alerts = []

        self.logger = getLogger(__name__)

    def run(self) -> None:
        self.logger.info('Automation process started')

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

                match1 = fullmatch(pattern1, basename)
                match2 = fullmatch(pattern2, basename)

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
                    strategy_instance = strategy.value(client, **params)
                    feeds = strategy_instance.params.get('feeds')
                    market_data = self.realtime_provider.fetch_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        feeds=feeds
                    )
                    strategy_instance.start(market_data)

                    strategy_context = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': strategy_instance,
                        'client': client,
                        'market_data': market_data,
                        'alerts': self.alerts,
                        'updated': False
                    }
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
                market_data = self.realtime_provider.fetch_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.interval,
                    feeds=feeds
                )
                strategy_instance.start(market_data)

                strategy_context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': strategy_instance,
                    'client': client,
                    'market_data': market_data,
                    'alerts': self.alerts,
                    'updated': False
                }
                context_id = str(id(strategy_context))
                self.strategy_contexts[context_id] = strategy_context
            except Exception:
                self.logger.exception('An error occurred')

        Thread(target=self._automate, daemon=True).start()

    def _automate(self) -> None:
        while True:
            for context_id, strategy_context in self.strategy_contexts.items():
                try:
                    if self.realtime_provider.update_data(strategy_context):
                        self._execute_strategy(context_id)
                        self._update_alerts(context_id)
                        strategy_context['updated'] = True
                except Exception:
                    self.logger.exception('An error occurred')

            sleep(1.0)

    def _execute_strategy(self, context_id: str) -> None:
        strategy_context = self.strategy_contexts[context_id]
        instance = strategy_context['instance']
        instance.start(strategy_context['market_data'])
        instance.trade()

    def _update_alerts(self, context_id: str) -> None:
        strategy_context = self.strategy_contexts[context_id]
        new_alerts = strategy_context['client'].alerts

        if not new_alerts:
            return

        self.alerts.extend(
            {**alert, 'id': context_id} 
            for alert in new_alerts
        )
        new_alerts.clear()