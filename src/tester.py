import warnings
import ast
import os
from typing import Any

from src.flask_app import FlaskApp
from src import BinanceClient
from src import BybitClient
from src import Registry
from src import DealKeywords
from src import Preprocessor


class Tester():
    def __init__(self, testing: dict[str, str]) -> None:
        self.strategies = dict()

        for strategy in Registry.data.values():
            folder_path = os.path.abspath(
                f'src/strategies/{strategy.name}/backtesting/'
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
                    f'src/strategies/{strategy.name}/backtesting/{name}'
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
                    client.get_data(symbol, interval, start, end)
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

            client.get_data(symbol, interval, start, end)
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

        self.frontend_main_data = {}
        self.frontend_lite_data = {}

        for key, data in self.strategies.items():
            frontend_data = self.get_frontend_data(data)
            self.frontend_main_data[key] = frontend_data[0]
            self.frontend_lite_data[key] = frontend_data[1]

    def update_strategy(
        self,
        strategy: str,
        parameter_name: str,
        new_value: Any
    ) -> None:
        try:
            parameters = self.strategies[strategy]['parameters']
            old_value = parameters[parameter_name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float) and isinstance(new_value, int):
                    new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise

            parameters[parameter_name] = new_value
            strategy_instance = (
                self.strategies[strategy]['instance'].__class__(
                    all_parameters=list(parameters.values())
                )
            )
            self.strategies[strategy]['instance'] = strategy_instance
            frontend_data = self.get_frontend_data(self.strategies[strategy])
            self.frontend_main_data[strategy] = frontend_data[0]
            self.frontend_lite_data[strategy] = frontend_data[1]
        except Exception:
            raise

    def get_frontend_data(self, data: dict) -> list[dict]:
        result = []
        data['instance'].start(data['client'])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            equity = data['instance'].get_equity(
                data['instance'].initial_capital,
                data['instance'].completed_deals_log
            )
            metrics = data['instance'].get_metrics(
                data['instance'].initial_capital,
                data['instance'].completed_deals_log
            )

        result.append({
            'chartData': {
                'name': data['name'].capitalize().replace('_', '-'),
                'exchange': data['exchange'],
                'symbol': data['symbol'],
                'interval': data['interval'],
                'mintick': data['mintick'],
                'klines': Preprocessor.get_klines(
                    data['client'].price_data
                ),
                'indicators': Preprocessor.get_indicators(
                    data['client'].price_data,
                    data['instance'].indicators
                ),
                'markers': Preprocessor.get_deals(
                    data['instance'].completed_deals_log,
                    data['instance'].open_deals_log,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                    data['instance'].qty_precision
                ),
            },
            'reportData': {
                'equity': Preprocessor.get_equity(equity),
                'metrics': metrics,
                'completedDealsLog': Preprocessor.get_completed_deals_log(
                    data['instance'].completed_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                ),
                'openDealsLog': Preprocessor.get_open_deals_log(
                    data['instance'].open_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals
                )
            }
        })
        result.append({
            'name': data['name'].capitalize().replace('_', '-'),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'interval': data['interval'],
            'mintick': data['mintick'],
            'parameters': data['parameters']
        })
        return result
        
    def start(self) -> None:
        self.app = FlaskApp(
            mode='testing',
            update_strategy=self.update_strategy,
            import_name='TVLite',
            static_folder="src/frontend/static",
            template_folder="src/frontend/templates",
        )
        self.app.set_main_data(self.frontend_main_data)
        self.app.set_lite_data(self.frontend_lite_data)
        self.app.run(host='0.0.0.0', port=8080)