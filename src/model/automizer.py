import ast
import glob
import logging
import os
import re
import threading

import numpy as np

import src.model.enums as enums
from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient


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
            path_to_folder = os.path.abspath(
                f'src/model/strategies/{strategy.name.lower()}/automation/'
            )
            filenames = glob.glob(f'{path_to_folder}/*.txt')

            for filename in filenames:
                pattern = r'(\w+)_(\w+)_(\w+)\.txt'
                exchange, symbol, interval = (
                    re.match(
                        pattern, filename[filename.rfind('\\') + 1 :]
                    ).groups()
                )
                exchange = exchange.lower()
                symbol = symbol.upper()

                if interval.isdigit():
                    interval = int(interval)

                if exchange == enums.Exchange.BINANCE.name.lower():
                    client = self.binance_client
                elif exchange == enums.Exchange.BYBIT.name.lower():
                    client = self.bybit_client

                with open(filename, 'r') as file:
                    parameters = []
                    
                    for line in file:
                        if '#' in line:
                            continue

                        parameters.append(
                            ast.literal_eval(
                                line[line.find('= ') + 2 :]
                            )
                        )

                raw_klines = client.fetch_last_klines(symbol, interval)
                klines = np.array(raw_klines)[:, :6].astype(float)
                p_precision = client.fetch_price_precision(symbol)
                q_precision = client.fetch_qty_precision(symbol)
                instance = strategy.value(all_params=parameters)
                strategy_data = {
                    'name': strategy.name,
                    'type': strategy.value,
                    'instance': instance,
                    'parameters': instance.__dict__.copy(),
                    'client': client,
                    'exchange': exchange,
                    'symbol': symbol,
                    'interval': interval,
                    'klines': klines,
                    'p_precision': p_precision,
                    'q_precision': q_precision,
                    'alerts': self.alerts,
                    'updated': False
                }
                instance.start(
                    {
                        'client': client,
                        'klines': klines,
                        'p_precision': p_precision,
                        'q_precision': q_precision,
                    }
                )
                self.strategies[str(id(strategy_data))] = strategy_data
        
        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            raw_klines = client.fetch_last_klines(self.symbol, self.interval)
            klines = np.array(raw_klines)[:, :6].astype(float)
            p_precision = client.fetch_price_precision(self.symbol)
            q_precision = client.fetch_qty_precision(self.symbol)
            instance = self.strategy.value()
            strategy_data = {
                'name': self.strategy.name,
                'type': self.strategy.value,
                'instance': instance,
                'parameters': instance.__dict__.copy(),
                'client': client,
                'exchange': self.exchange.value.lower(),
                'symbol': self.symbol,
                'interval': self.interval.value,
                'klines': klines,
                'p_precision': p_precision,
                'q_precision': q_precision,
                'alerts': self.alerts,
                'updated': False
            }
            instance.start(
                {
                    'client': client,
                    'klines': klines,
                    'p_precision': p_precision,
                    'q_precision': q_precision,
                }
            )
            self.strategies[str(id(strategy_data))] = strategy_data

        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self) -> None:
        while True:
            for strategy_id, strategy_data in self.strategies.items():
                raw_klines = strategy_data['client'].fetch_last_klines(
                    symbol=strategy_data['symbol'],
                    interval=strategy_data['interval'],
                    limit=2
                )
                new_klines = np.array(raw_klines)[:, :6].astype(float)

                if new_klines.shape[0] == 0:
                    continue

                last_kline_time = strategy_data['klines'][-1, 0]
                new_kline_time = new_klines[-1, 0]

                if new_kline_time > last_kline_time:
                    strategy_data['klines'] = np.vstack(
                        [strategy_data['klines'], new_klines[-1]]
                    )
                    strategy_data['instance'].start(
                        {
                            'client': strategy_data['client'],
                            'klines': strategy_data['klines'],
                            'p_precision': strategy_data['p_precision'],
                            'q_precision': strategy_data['q_precision'],
                        }
                    )
                    strategy_data['instance'].trade(strategy_data['symbol'])
                    strategy_data['updated'] = True

                    if strategy_data['client'].alerts:
                        for alert in strategy_data['client'].alerts:
                            alert['id'] = strategy_id
                            self.alerts.append(alert)

                        strategy_data['client'].alerts.clear()