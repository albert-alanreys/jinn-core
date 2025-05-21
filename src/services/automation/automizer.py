import json
import os
from glob import glob
from logging import getLogger
from re import fullmatch
from threading import Thread

import src.core.enums as enums
from .realtime_data_provider import RealtimeDataProvider
from .api_clients.binance import BinanceREST
from .api_clients.bybit import BybitREST


class Automizer():
    def __init__(self, automation_info: dict) -> None:
        self.exchange = automation_info['exchange']
        self.symbol = automation_info['symbol']
        self.interval = automation_info['interval']
        self.strategy = automation_info['strategy']

        self.strategies = {}
        self.alerts = []

        self.data_provider = RealtimeDataProvider()
        self.binance_client = BinanceREST()
        self.bybit_client = BybitREST()

        self.logger = getLogger(__name__)

    def automate(self) -> None:
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
                    exchange, symbol, _, interval = (
                        match2.group(1).upper(),
                        match2.group(2).upper(),
                        match2.group(3),
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

                valid_interval = client.get_valid_interval(interval)

                try:
                    market_data = self.data_provider.get_data(
                        client=client,
                        symbol=symbol,
                        interval=valid_interval
                    )
                    instance = strategy.value(client, **params)
                    instance.start(market_data)

                    strategy_data = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': instance,
                        'params': instance.params,
                        'client': client,
                        'exchange': exchange,
                        'interval': valid_interval,
                        'alerts': self.alerts,
                        'klines_updated': False,
                        'alerts_updated': False,
                        **market_data
                    }
                    strategy_id = str(id(strategy_data))
                    self.strategies[strategy_id] = strategy_data
                except Exception as e:
                    self.logger.error(
                        msg=f'{type(e).__name__} - {e}',
                        exc_info=True
                    )

        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            self.valid_interval = client.get_valid_interval(self.interval)

            try:
                market_data = self.data_provider.get_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.valid_interval
                )
                instance = strategy.value(client)
                instance.start(market_data)

                strategy_data = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'params': instance.params,
                    'client': client,
                    'exchange': self.exchange.value,
                    'interval': self.valid_interval,
                    'alerts': self.alerts,
                    'klines_updated': False,
                    'alerts_updated': False,
                    **market_data
                }
                strategy_id = str(id(strategy_data))
                self.strategies[strategy_id] = strategy_data
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}', exc_info=True)

        self.data_provider.subscribe_kline_updates(self.strategies)
        Thread(target=self._run_automation, daemon=True).start()

    def _run_automation(self) -> None:
        while True:
            try:
                for strategy_id, strategy_data in self.strategies.items():
                    if strategy_data['klines_updated']:
                        strategy_data['klines_updated'] = False
                        market_data = {
                            'market': strategy_data['market'],
                            'symbol': strategy_data['symbol'],
                            'klines': strategy_data['klines'],
                            'p_precision': strategy_data['p_precision'],
                            'q_precision': strategy_data['q_precision']
                        }
                        strategy_data['instance'].start(market_data)
                        strategy_data['instance'].trade()
                        strategy_data['alerts_updated'] = True

                        if strategy_data['client'].alerts:
                            for alert in strategy_data['client'].alerts:
                                alert['id'] = strategy_id
                                self.alerts.append(alert)

                            strategy_data['client'].alerts.clear()
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}', exc_info=True)