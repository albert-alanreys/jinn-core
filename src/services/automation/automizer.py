import glob
import json
import logging
import os
import re
import threading

import numpy as np

import src.core.enums as enums
from .api_clients.binance import BinanceClient
from .api_clients.bybit import BybitClient


class Automizer():
    def __init__(self, automation_info: dict) -> None:
        self.exchange = automation_info['exchange']
        self.symbol = automation_info['symbol']
        self.interval = automation_info['interval']
        self.strategy = automation_info['strategy']

        self.strategies = {}
        self.alerts = []

        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.logger = logging.getLogger(__name__)

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
            file_paths = glob.glob(f'{folder_path}/*.json')

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
                                f'Failed to parse JSON {file_path}'
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
                                f'Failed to parse JSON {file_path}'
                            )
                            continue

                match exchange:
                    case enums.Exchange.BINANCE.name:
                        client = self.binance_client
                    case enums.Exchange.BYBIT.name:
                        client = self.bybit_client

                valid_interval = client.get_valid_interval(interval)

                try:
                    data = client.get_last_klines(
                        symbol=symbol,
                        interval=valid_interval,
                        limit=3000
                    )
                    klines = np.array(data)[:, :6].astype(float)
                    p_precision = client.get_price_precision(symbol)
                    q_precision = client.get_qty_precision(symbol)

                    market_data = {
                        'market': enums.Market.FUTURES,
                        'symbol': symbol,
                        'klines': klines,
                        'p_precision': p_precision,
                        'q_precision': q_precision
                    }

                    instance = strategy.value(**params)
                    instance.start(client=client, market_data=market_data)

                    strategy_data = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': instance,
                        'params': instance.params,
                        'client': client,
                        'exchange': exchange,
                        'interval': valid_interval,
                        'alerts': self.alerts,
                        'updated': False,
                        **market_data
                    }
                    self.strategies[str(id(strategy_data))] = strategy_data
                except Exception as e:
                    self.logger.error(f'{type(e).__name__} - {e}')

        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            self.valid_interval = client.get_valid_interval(self.interval)

            try:
                data = client.get_last_klines(
                    symbol=self.symbol,
                    interval=self.valid_interval,
                    limit=3000
                )
                klines = np.array(data)[:, :6].astype(float)
                p_precision = client.get_price_precision(self.symbol)
                q_precision = client.get_qty_precision(self.symbol)

                market_data = {
                    'market': enums.Market.FUTURES,
                    'symbol': self.symbol,
                    'klines': klines,
                    'p_precision': p_precision,
                    'q_precision': q_precision
                }
                instance = self.strategy.value()
                instance.start(client, market_data)

                strategy_data = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'params': instance.params,
                    'client': client,
                    'exchange': self.exchange.value,
                    'interval': self.valid_interval,
                    'alerts': self.alerts,
                    'updated': False,
                    **market_data
                }
                self.strategies[str(id(strategy_data))] = strategy_data
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}')

        thread = threading.Thread(target=self._run_automation, daemon=True)
        thread.start()

    def _run_automation(self) -> None:
        while True:
            for strategy_id, strategy_data in self.strategies.items():
                raw_klines = strategy_data['client'].get_last_klines(
                    symbol=strategy_data['symbol'],
                    interval=strategy_data['interval'],
                    limit=2
                )

                if len(raw_klines) < 2:
                    continue

                new_klines = np.array(raw_klines)[:-1, :6].astype(float)
                last_kline_time = strategy_data['klines'][-1, 0]
                new_kline_time = new_klines[-1, 0]

                if new_kline_time > last_kline_time:
                    strategy_data['klines'] = np.vstack(
                        [strategy_data['klines'], new_klines[-1]]
                    )
                    market_data = {
                        'market': strategy_data['market'],
                        'symbol': strategy_data['symbol'],
                        'klines': strategy_data['klines'],
                        'p_precision': strategy_data['p_precision'],
                        'q_precision': strategy_data['q_precision']
                    }
                    strategy_data['instance'].start(
                        client=strategy_data['client'],
                        market_data=market_data
                    )
                    strategy_data['instance'].trade()
                    strategy_data['updated'] = True

                    if strategy_data['client'].alerts:
                        for alert in strategy_data['client'].alerts:
                            alert['id'] = strategy_id
                            self.alerts.append(alert)

                        strategy_data['client'].alerts.clear()