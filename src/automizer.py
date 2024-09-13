import threading
import ast
import os

from src.flask_app import FlaskApp
import src.deal_keywords as dk
import src.preprocessor as pp


class Automizer():
    def __init__(self, automation, http_clients, strategies):
        self.strategies = dict()

        for strategy in strategies.values():
            folder_path = os.path.abspath(
                'src/strategies/' + strategy['name'] + '/automation/'
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
                    http_client = http_clients[0]()
                elif exchange.lower() == 'bybit':
                    http_client = http_clients[1]()

                file_path = os.path.abspath(
                    'src/strategies/' + strategy['name'] +
                    '/automation/' + name
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

                http_client.get_data(symbol, interval)
                strategy_obj = strategy['class'](
                    http_client, all_parameters=parameters
                )
                all_parameters = strategy_obj.__dict__.copy()
                del all_parameters['http_client']

                strategy_data = {
                    'name': strategy['name'],
                    'exchange': exchange.lower(),
                    'symbol': symbol,
                    'interval': interval,
                    'mintick': http_client.price_precision,
                    'strategy': strategy_obj,
                    'parameters': all_parameters,
                    'http_client': http_client
                }
                self.strategies[str(id(strategy_data))] = strategy_data
        
        if len(self.strategies) == 0:
            exchange = automation['exchange']
            symbol = automation['symbol']
            interval = automation['interval']

            if exchange.lower() == 'binance':
                http_client = http_clients[0]()
            elif exchange.lower() == 'bybit':
                http_client = http_clients[1]()

            http_client.get_data(symbol, interval)
            strategy_obj = strategies[
                automation['strategy']
            ]['class'](http_client)
            all_parameters = strategy_obj.__dict__.copy()
            del all_parameters['http_client']

            strategy_data = {
                'name': strategies[automation['strategy']]['name'],
                'exchange': exchange.lower(),
                'symbol': symbol,
                'interval': interval,
                'mintick': http_client.price_precision,
                'strategy': strategy_obj,
                'parameters': all_parameters,
                'http_client': http_client
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
                if data['http_client'].update_data():
                    frontend_data = self.get_frontend_data(data)
                    self.frontend_main_data[key] = frontend_data[0]
                    self.frontend_lite_data[key] = frontend_data[1]
                    self.app.set_main_data(self.frontend_main_data)
                    self.app.set_lite_data(self.frontend_lite_data)
                    self.app.set_data_updates(key)
                    data['strategy'].trade()

                    if len(data['http_client'].alerts) > 0:
                        for alert in data['http_client'].alerts:
                            alert['strategy'] = key
                            self.alerts.append(alert)

                        self.app.set_alert_updates(self.alerts)
                        data['http_client'].alerts.clear()
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
                self.strategies[strategy]['strategy'].http_client,
                all_parameters=list(
                    self.strategies[strategy]['parameters'].values()
                )
            )
            self.strategies[strategy]['strategy'] = strategy_obj
            frontend_data = self.get_frontend_data(self.strategies[strategy])
            self.frontend_main_data[strategy] = frontend_data[0]
            self.frontend_lite_data[strategy] = frontend_data[1]
        except:
            raise

        self.thread.do_run = True

    def get_frontend_data(self, data):
        result = []

        data['strategy'].start()
        completed_deals_log = data['strategy'] \
            .completed_deals_log.reshape((-1, 13))
        open_deals_log = data['strategy'].open_deals_log

        result.append({
            'chartData': {
                'name': data['name'].capitalize().replace('_', '-'),
                'exchange': data['exchange'],
                'symbol': data['symbol'],
                'interval': data['interval'],
                'mintick': data['mintick'],
                'klines': pp.preprocess_klines(
                    data['strategy'].http_client.price_data
                ),
                'indicators': pp.preprocess_indicators(
                    data['strategy'].http_client.price_data,
                    data['strategy'].indicators
                ),
                'markers': pp.preprocess_deals(
                    completed_deals_log,
                    open_deals_log,
                    dk.entry_signal_keywords,
                    dk.exit_signal_keywords,
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