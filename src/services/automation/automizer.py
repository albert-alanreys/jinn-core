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

                try:
                    strategy_instance = strategy.value(client, **params)
                    feeds = strategy_instance.params.get('feeds')
                    market_data = self.realtime_provider.fetch_data(
                        client=client,
                        symbol=symbol,
                        interval=interval,
                        extra_feeds=feeds
                    )
                    strategy_instance.start(market_data)

                    strategy_state = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': strategy_instance,
                        'client': client,
                        'alerts': self.alerts,
                        'klines_updated': False,
                        'alerts_updated': False,
                        'market_data': market_data
                    }
                    strategy_id = str(id(strategy_state))
                    self.strategy_states[strategy_id] = strategy_state
                except Exception:
                    self.logger.exception('An error occurred')

        if not self.strategy_states:
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
                    extra_feeds=feeds
                )
                strategy_instance.start(market_data)

                strategy_state = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': strategy_instance,
                    'client': client,
                    'alerts': self.alerts,
                    'klines_updated': False,
                    'alerts_updated': False,
                    'market_data': market_data
                }
                strategy_id = str(id(strategy_state))
                self.strategy_states[strategy_id] = strategy_state
            except Exception:
                self.logger.exception('An error occurred')

        self.realtime_provider.subscribe_kline_updates(self.strategy_states)
        Thread(target=self._run_automation, daemon=True).start()

    def _run_automation(self) -> None:
        while True:
            for strategy_id, strategy_state in self.strategy_states.items():
                if not strategy_state['klines_updated']:
                    continue

                if not self._all_extra_klines_updated(strategy_id):
                    continue

                strategy_state['klines_updated'] = False

                try:
                    self._execute_strategy(strategy_id)
                    self._update_alerts(strategy_id)
                except Exception:
                    self.logger.exception('An error occurred')

    def _all_extra_klines_updated(self, strategy_id: str) -> bool:
        strategy_state = self.strategy_states[strategy_id]
        market_data = strategy_state['market_data']
        base_klines = market_data['klines']
        extra_klines_by_feed = market_data['extra_klines']

        if not extra_klines_by_feed:
            return True

        try:
            base_duration = base_klines[1][0] - base_klines[0][0]
            expected_close_time = base_klines[-1][0] + base_duration

            for extra_klines in extra_klines_by_feed.values():
                duration = extra_klines[1][0] - extra_klines[0][0]
                open_time = extra_klines[-1][0]

                if expected_close_time == open_time + 2 * duration:
                    return False
                elif expected_close_time > open_time + 2 * duration:
                    self.logger.warning('Data synchronization error')
                    return False
        except Exception:
            self.logger.exception('An error occurred')
            return False

        return True

    def _execute_strategy(self, strategy_id: str) -> None:
        strategy_state = self.strategy_states[strategy_id]
        instance = strategy_state['instance']
        instance.start(strategy_state['market_data'])
        instance.trade()

    def _update_alerts(self, strategy_id: str) -> None:
        strategy_state = self.strategy_states[strategy_id]
        alerts = strategy_state['client'].alerts

        if alerts:
            for alert in alerts:
                alert['id'] = strategy_id
                self.alerts.append(alert)

            alerts.clear()

        strategy_state['alerts_updated'] = True