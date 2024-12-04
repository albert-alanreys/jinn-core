import threading
import ast
import os

from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient
from src.model.strategies.registry import Registry


class Automizer():
    def __init__(self, automation: dict[str, str]) -> None:
        self.strategies = dict()
        self.alerts = []

        for strategy in Registry.data.values():
            folder_path = os.path.abspath(
                f'src/model/strategies/{strategy.name}/automation/'
            )
            file_names = os.listdir(folder_path)

            for name in file_names.copy():
                if not name.endswith('.txt'):
                    file_names.remove(name)

            for name in file_names:
                exchange = name[:name.find('_')]
                symbol = name[
                    name.find('_', name.find('_')) + 1 : name.rfind('_')
                ]
                interval = name[
                    name.rfind('_') + 1 : name.rfind('.')
                ]

                if exchange.lower() == 'binance':
                    interval = BinanceClient.intervals[interval]
                    client = BinanceClient()
                elif exchange.lower() == 'bybit':
                    interval = BybitClient.intervals[interval]
                    client = BybitClient()

                file_path = os.path.abspath(
                    f'src/model/strategies/{strategy.name}/automation/{name}'
                )

                with open(file_path, 'r') as file:
                    parameters = []
                    
                    for line in file:
                        if '#' in line:
                            continue

                        parameters.append(
                            ast.literal_eval(
                                line[line.find('= ') + 2 :]
                            )
                        )

                client.get_klines(symbol, interval)
                strategy_instance = strategy.type(
                    all_parameters=parameters
                )
                all_parameters = strategy_instance.__dict__.copy()
                all_parameters.pop('_abc_impl')
                strategy_data = {
                    'name': strategy.name,
                    'instance': strategy_instance,
                    'client': client,
                    'parameters': all_parameters,
                    'exchange': exchange.lower(),
                    'symbol': symbol,
                    'interval': interval,
                    'mintick': client.price_precision,
                    'alerts': self.alerts,
                    'updated': False
                }
                self.strategies[str(id(strategy_data))] = strategy_data
        
        if len(self.strategies) == 0:
            exchange = automation['exchange']
            symbol = automation['symbol']
            interval = automation['interval']

            if exchange.lower() == 'binance':
                interval = BinanceClient.intervals[interval]
                client = BinanceClient()
            elif exchange.lower() == 'bybit':
                interval = BybitClient.intervals[interval]
                client = BybitClient()

            client.get_klines(symbol, interval)
            strategy_instance = Registry.data[
                automation['strategy']
            ].type()
            all_parameters = strategy_instance.__dict__.copy()
            all_parameters.pop('_abc_impl')
            strategy_data = {
                'name': Registry.data[automation['strategy']].name,
                'instance': strategy_instance,
                'client': client,
                'parameters': all_parameters,
                'exchange': exchange.lower(),
                'symbol': symbol,
                'interval': interval,
                'mintick': client.price_precision,
                'alerts': self.alerts,
                'updated': False
            }
            self.strategies[str(id(strategy_data))] = strategy_data

    def update(self) -> None:
        while True:
            for id, data in self.strategies.items():
                if data['client'].update_data(
                    data['symbol'], data['interval']
                ):
                    data['instance'].start(data['client'])
                    data['instance'].trade(data['symbol'])
                    data['updated'] = True

                    if data['client'].alerts:
                        for alert in data['client'].alerts:
                            alert['id'] = id
                            self.alerts.append(alert)

                        data['client'].alerts.clear()

    def start(self) -> None:
        self.thread = threading.Thread(target=self.update)
        self.thread.start()