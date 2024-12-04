import ast
import glob
import logging
import os
import warnings

import numpy as np

import src.model.enums as enums
from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient
from src.model.db_manager import DBManager


class Tester():
    def __init__(self, testing_info: dict) -> None:
        self.exchange = testing_info['exchange']
        self.market = testing_info['market']
        self.symbol = testing_info['symbol']
        self.interval = testing_info['interval']
        self.start = testing_info['start']
        self.end = testing_info['end']
        self.strategy = testing_info['strategy']

        self.db_manager = DBManager()
        self.binance_client = None
        self.bybit_client = BybitClient()

        self.logger = logging.getLogger(__name__)

    def test(self) -> None:
        self.strategies = dict()

        for strategy in enums.Strategy:
            path_to_folder = os.path.abspath(
                f'src/model/strategies/{strategy.name.lower()}/backtesting/'
            )
            files = glob.glob(f'{path_to_folder}/*.txt')

            for file in files:
                exchange = file[:file.find('_')]
                symbol = file[
                    file.find('_', file.find('_')) + 1 : file.rfind('_')
                ]
                interval = file[
                    file.rfind('_') + 1 : file.rfind('.')
                ]

                match exchange.lower():
                    case enums.Exchange.BINANCE.name.lower():
                        client = self.binance_client
                    case enums.Exchange.BYBIT.name.lower():
                        client = self.bybit_client

                path_to_file = os.path.abspath(
                    f'src/model/strategies/{strategy.file}/backtesting/{file}'
                )
                target_line = False
                opt_parameters = []
                parameters = []

                with open(path_to_file, 'r') as file:
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
                    match self.market:
                        case enums.Market.SPOT:
                            postfix = '_SPOT'
                        case enums.Market.FUTURES:
                            postfix = '_FUTURES'

                    rows, _ = self.db_manager.fetch_data(
                        db_name=f'{exchange.capitalize()}.db',
                        table=f'{symbol}{postfix}_{interval}',
                        start=start,
                        end=end
                    )
                    klines = np.array(rows)
                    price_precision = client.fetch_price_precision(symbol)
                    qty_precision = client.fetch_qty_precision(symbol)
                    strategy_instance = strategy.value(
                        opt_parameters=parameters
                    )
                    equity, metrics = self.calculate_strategy(
                        {
                            'instance': strategy_instance,
                            'client': client,
                            'klines': klines,
                            'price_precision': price_precision,
                            'qty_precision': qty_precision,
                        }
                    )
                    strategy_data = {
                        'name': strategy.name,
                        'instance': strategy_instance,
                        'parameters': strategy_instance.__dict__.copy(),
                        'equity': equity,
                        'metrics': metrics,
                        'client': client,
                        'exchange': exchange.lower(),
                        'symbol': symbol,
                        'interval': interval,
                        'klines': klines,
                        'price_precision': price_precision,
                        'qty_precision': qty_precision,
                    }
                    self.strategies[str(id(strategy_data))] = strategy_data

        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            match self.market:
                case enums.Market.SPOT:
                    postfix = '_SPOT'
                case enums.Market.FUTURES:
                    postfix = '_FUTURES'

            rows, _ = self.db_manager.fetch_data(
                db_name=f'{self.exchange.value.capitalize()}.db',
                table=f'{self.symbol}{postfix}_{self.interval.value}',
                start=self.start,
                end=self.end
            )
            klines = np.array(rows)
            price_precision = client.fetch_price_precision(self.symbol)
            qty_precision = client.fetch_qty_precision(self.symbol)
            strategy_instance = self.strategy.value()
            equity, metrics = self.calculate_strategy(
                {
                    'instance': strategy_instance,
                    'client': client,
                    'klines': klines,
                    'price_precision': price_precision,
                    'qty_precision': qty_precision,
                }
            )
            strategy_data = {
                'name': self.strategy.name,
                'instance': strategy_instance,
                'parameters': strategy_instance.__dict__.copy(),
                'equity': equity,
                'metrics': metrics,
                'client': client,
                'exchange': self.exchange.value.lower(),
                'symbol': self.symbol,
                'interval': self.interval.value,
                'klines': klines,
                'price_precision': price_precision,
                'qty_precision': qty_precision,
            }
            self.strategies[str(id(strategy_data))] = strategy_data

    def calculate_strategy(self, data: dict) -> tuple:
        self.logger.info(f"Testing strategy:\n{data['instance']}")

        data['instance'].start(
            {
                'client': data['client'],
                'klines': data['klines'],
                'price_precision': data['price_precision'],
                'qty_precision': data['qty_precision'],
            }
        )

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

        return equity, metrics