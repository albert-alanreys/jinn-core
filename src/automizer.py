import threading
import ast
import os

from src.flask_app import FlaskApp
from src import BinanceClient
from src import BybitClient
from src import Strategies
from src import DealKeywords
from src import Preprocessor


class Automizer():
    def __init__(self, automation):
        self.strategies = dict()

        for strategy in Strategies.registry.values():
            folder_path = os.path.abspath(
                f'src/strategies/{strategy[0]}/automation/'
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
                    f'src/strategies/{strategy[0]}/automation/{name}'
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

                client.get_data(symbol, interval)
                strategy_obj = strategy[1](
                    client, all_parameters=parameters
                )
                all_parameters = strategy_obj.__dict__.copy()
                all_parameters.pop('client')
                strategy_data = {
                    'name': strategy[0],
                    'exchange': exchange.lower(),
                    'symbol': symbol,
                    'interval': interval,
                    'mintick': client.price_precision,
                    'strategy': strategy_obj,
                    'parameters': all_parameters,
                    'client': client
                }
                self.strategies[str(id(strategy_data))] = strategy_data
        
        if len(self.strategies) == 0:
            exchange = automation['exchange']
            symbol = automation['symbol']
            interval = automation['interval']

            if exchange.lower() == 'binance':
                client = BinanceClient()
            elif exchange.lower() == 'bybit':
                client = BybitClient()

            client.get_data(symbol, interval)
            strategy_obj = Strategies.registry[
                automation['strategy']
            ][1](client)
            all_parameters = strategy_obj.__dict__.copy()
            all_parameters.pop('client')
            strategy_data = {
                'name': Strategies.registry[automation['strategy']][0],
                'exchange': exchange.lower(),
                'symbol': symbol,
                'interval': interval,
                'mintick': client.price_precision,
                'strategy': strategy_obj,
                'parameters': all_parameters,
                'client': client
            }
            self.strategies[str(id(strategy_data))] = strategy_data

        self.frontend_main_data = {}
        self.frontend_lite_data = {}
        self.alerts = []

        for key, data in self.strategies.items():
            frontend_data = self.get_frontend_data(data)
            self.frontend_main_data[key] = frontend_data[0]
            self.frontend_lite_data[key] = frontend_data[1]

    def update(self):
        while True:
            if not getattr(self.thread, "do_run"):
                continue

            for key, data in self.strategies.items():
                if data['client'].update_data():
                    frontend_data = self.get_frontend_data(data)
                    self.frontend_main_data[key] = frontend_data[0]
                    self.frontend_lite_data[key] = frontend_data[1]
                    self.app.set_main_data(self.frontend_main_data)
                    self.app.set_lite_data(self.frontend_lite_data)
                    self.app.set_data_updates(key)
                    data['strategy'].trade()

                    if len(data['client'].alerts) > 0:
                        for alert in data['client'].alerts:
                            alert['strategy'] = key
                            self.alerts.append(alert)

                        self.app.set_alert_updates(self.alerts)
                        data['client'].alerts.clear()
                        self.alerts.clear()

    def update_strategy(self, strategy, name, new_value):
        self.thread.do_run = False

        try:
            old_value = self.strategies[strategy]['parameters'][name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float) and isinstance(new_value, int):
                    new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise
            
            self.strategies[strategy]['parameters'][name] = new_value
            strategy_obj = self.strategies[strategy]['strategy'].__class__(
                self.strategies[strategy]['strategy'].client,
                all_parameters=list(
                    self.strategies[strategy]['parameters'].values()
                )
            )
            self.strategies[strategy]['strategy'] = strategy_obj
            frontend_data = self.get_frontend_data(self.strategies[strategy])
            self.frontend_main_data[strategy] = frontend_data[0]
            self.frontend_lite_data[strategy] = frontend_data[1]
        except Exception:
            raise

        self.thread.do_run = True

    def get_frontend_data(self, data):
        result = []
        data['strategy'].start()
        completed_deals_log = (
            data['strategy'].completed_deals_log.reshape((-1, 13))
        )
        open_deals_log = data['strategy'].open_deals_log
        result.append({
            'chartData': {
                'name': data['name'].capitalize().replace('_', '-'),
                'exchange': data['exchange'],
                'symbol': data['symbol'],
                'interval': data['interval'],
                'mintick': data['mintick'],
                'klines': Preprocessor.get_klines(
                    data['strategy'].client.price_data
                ),
                'indicators': Preprocessor.get_indicators(
                    data['strategy'].client.price_data,
                    data['strategy'].indicators
                ),
                'markers': Preprocessor.get_deals(
                    completed_deals_log,
                    open_deals_log,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                    data['strategy'].qty_precision
                ),
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

    def start(self):
        self.thread = threading.Thread(target=self.update)
        self.thread.do_run = True
        self.thread.start()

        self.app = FlaskApp(
            mode='automation',
            update_strategy=self.update_strategy,
            import_name='TVLite',
            static_folder="src/frontend/static",
            template_folder="src/frontend/templates",
        )
        self.app.set_main_data(self.frontend_main_data)
        self.app.set_lite_data(self.frontend_lite_data)
        self.app.run(host='0.0.0.0', port=8080)