import ast
import os

from src.model.exchanges.binance_client import BinanceClient
from src.model.exchanges.bybit_client import BybitClient
from src.model.strategies.registry import Registry


class Tester():
    def __init__(self, testing: dict[str, str]) -> None:
        self.strategies = dict()

        for strategy in Registry.data.values():
            folder_path = os.path.abspath(
                f'src/model/strategies/{strategy.name}/backtesting/'
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
                    client = BinanceClient()
                elif exchange.lower() == 'bybit':
                    client = BybitClient()

                file_path = os.path.abspath(
                    f'src/model/strategies/{strategy.name}/backtesting/{name}'
                )
                target_line = False
                opt_parameters = []
                parameters = []

                with open(file_path, 'r') as file:
                    for line_num, line in enumerate(file):
                        if line_num == 0:
                            start = line[:line.find(' - ')].lstrip('Period: ')
                            end = line[
                                line.find(' - ') + 3 : line.find('\n')
                            ]

                        if target_line and line.startswith('='):
                            opt_parameters.append(parameters.copy())
                            parameters.clear()
                            target_line = False
                            continue

                        if target_line:
                            parameters.append(
                                ast.literal_eval(
                                    line[line.find('= ') + 2 :]
                                )
                            )

                        if line.startswith('='):
                            target_line = True

                for parameters in opt_parameters:
                    client.get_klines(symbol, interval, start, end)
                    strategy_instance = strategy.type(
                        opt_parameters=parameters
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
                        'mintick': client.price_precision
                    }
                    self.strategies[str(id(strategy_data))] = strategy_data

        if len(self.strategies) == 0:
            exchange = testing['exchange']
            symbol = testing['symbol']
            interval = testing['interval']
            start = testing['date/time #1']
            end = testing['date/time #2']

            if exchange == 'binance':
                client =  BinanceClient()
            elif exchange == 'bybit':
                client = BybitClient()

            client.get_klines(symbol, interval, start, end)
            strategy_instance = Registry.data[
                testing['strategy']
            ].type()
            all_parameters = strategy_instance.__dict__.copy()
            all_parameters.pop('_abc_impl')
            strategy_data = {
                'name': Registry.data[testing['strategy']].name,
                'instance': strategy_instance,
                'client': client,
                'parameters': all_parameters,
                'exchange': exchange.lower(),
                'symbol': symbol,
                'interval': interval,
                'mintick': client.price_precision
            }
            self.strategies[str(id(strategy_data))] = strategy_data