import json
import os
from glob import glob
from logging import getLogger
from re import fullmatch
from threading import Thread

import src.core.enums as enums
from .realtime_provider import RealtimeProvider
from .api_clients.binance import BinanceREST
from .api_clients.bybit import BybitREST


class Automizer():
    def __init__(self, automation_info: dict) -> None:
        self.exchange = automation_info['exchange']
        self.symbol = automation_info['symbol']
        self.interval = automation_info['interval']
        self.strategy = automation_info['strategy']

        self.realtime_provider = RealtimeProvider()
        self.binance_client = BinanceREST()
        self.bybit_client = BybitREST()

        self.strategy_states = {}
        self.alerts = []

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

                valid_interval = client.get_valid_interval(interval)

                try:
                    market_data = self.realtime_provider.fetch_data(
                        client=client,
                        symbol=symbol,
                        interval=valid_interval
                    )
                    strategy_instance = strategy.value(client, **params)
                    strategy_instance.start(market_data)

                    strategy_state = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': strategy_instance,
                        'params': strategy_instance.params,
                        'client': client,
                        'alerts': self.alerts,
                        'klines_updated': False,
                        'alerts_updated': False,
                        'market_data': market_data
                    }
                    strategy_id = str(id(strategy_state))
                    self.strategy_states[strategy_id] = strategy_state
                except Exception as e:
                    self.logger.error(
                        msg=f'{type(e).__name__} - {e}',
                        exc_info=True
                    )

        if not self.strategy_states:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            self.valid_interval = client.get_valid_interval(self.interval)

            try:
                market_data = self.realtime_provider.fetch_data(
                    client=client,
                    symbol=self.symbol,
                    interval=self.valid_interval
                )
                strategy_instance = strategy.value(client)
                strategy_instance.start(market_data)

                strategy_state = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': strategy_instance,
                    'params': strategy_instance.params,
                    'client': client,
                    'alerts': self.alerts,
                    'klines_updated': False,
                    'alerts_updated': False,
                    'market_data': market_data
                }
                strategy_id = str(id(strategy_state))
                self.strategy_states[strategy_id] = strategy_state
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}', exc_info=True)

        self.realtime_provider.subscribe_kline_updates(self.strategy_states)
        Thread(target=self._run_automation, daemon=True).start()

    def _run_automation(self) -> None:
        while True:
            try:
                for strategy_id, strategy_state in self.strategy_states.items():
                    if strategy_state['klines_updated']:
                        strategy_state['klines_updated'] = False
                        strategy_state['instance'].start(
                            strategy_state['market_data']
                        )
                        strategy_state['instance'].trade()
                        strategy_state['alerts_updated'] = True

                        if strategy_state['client'].alerts:
                            for alert in strategy_state['client'].alerts:
                                alert['id'] = strategy_id
                                self.alerts.append(alert)

                            strategy_state['client'].alerts.clear()
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}', exc_info=True)