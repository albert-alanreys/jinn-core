import ast
import glob
import logging
import os
import re
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

        self.strategies = {}
        self.db_manager = DBManager()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.logger = logging.getLogger(__name__)

    def test(self) -> None:
        self.logger.info('Testing process started')

        for strategy in enums.Strategy:
            path_to_folder = os.path.abspath(
                f'src/model/strategies/{strategy.name.lower()}/backtesting/'
            )
            filenames = glob.glob(f'{path_to_folder}/*.txt')

            for filename in filenames:
                pattern = r'(\w+)_(\w+)_(\w+)_(\w+)\.txt'
                exchange, symbol, market, interval = (
                    re.match(
                        pattern, filename[filename.rfind('\\') + 1 :]
                    ).groups()
                )

                if exchange.upper() == enums.Exchange.BINANCE.name:
                    client = self.binance_client
                elif exchange.upper() == enums.Exchange.BYBIT.name:
                    client = self.bybit_client

                target_line = False
                opt_params = []
                parameters = []

                with open(filename, 'r') as file:
                    for line_num, line in enumerate(file):
                        if line_num == 0:
                            start = line[:line.find(' - ')].lstrip('Period: ')
                            end = line[
                                line.find(' - ') + 3 : line.find('\n')
                            ]

                        if target_line and line.startswith('='):
                            opt_params.append(parameters.copy())
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

                for parameters in opt_params:
                    interval = client.get_valid_interval(interval)
                    rows, _ = self.db_manager.fetch_data(
                        db_name=f'{exchange.lower()}.db',
                        table=f'{symbol}_{market}_{interval}',
                        start=start,
                        end=end
                    )
                    klines = np.array(rows)
                    p_precision = client.get_price_precision(symbol)
                    q_precision = client.get_qty_precision(symbol)
                    instance = strategy.value(opt_params=parameters)
                    strategy_data = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'instance': instance,
                        'parameters': instance.__dict__.copy(),
                        'client': client,
                        'exchange': exchange,
                        'symbol': symbol,
                        'market': market,
                        'interval': interval,
                        'klines': klines,
                        'p_precision': p_precision,
                        'q_precision': q_precision,
                    }
                    equity, metrics = self.calculate_strategy(strategy_data)
                    strategy_data['equity'] = equity
                    strategy_data['metrics'] = metrics
                    self.strategies[str(id(strategy_data))] = strategy_data

        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            match self.market:
                case enums.Market.SPOT:
                    market = 'SPOT'
                case enums.Market.FUTURES:
                    market = 'FUTURES'

            self.interval = client.get_valid_interval(self.interval)
            rows, _ = self.db_manager.fetch_data(
                db_name=f'{self.exchange.value.lower()}.db',
                table=f'{self.symbol}_{market}_{self.interval}',
                start=self.start,
                end=self.end
            )
            klines = np.array(rows)
            p_precision = client.get_price_precision(self.symbol)
            q_precision = client.get_qty_precision(self.symbol)
            instance = self.strategy.value()
            strategy_data = {
                'name': self.strategy.name,
                'type': self.strategy.value,
                'instance': instance,
                'parameters': instance.__dict__.copy(),
                'client': client,
                'exchange': self.exchange.value,
                'symbol': self.symbol,
                'market': market,
                'interval': self.interval,
                'klines': klines,
                'p_precision': p_precision,
                'q_precision': q_precision,
            }
            equity, metrics = self.calculate_strategy(strategy_data)
            strategy_data['equity'] = equity
            strategy_data['metrics'] = metrics
            self.strategies[str(id(strategy_data))] = strategy_data

    def calculate_strategy(self, strategy_data: dict) -> tuple:
        strategy_data['instance'].start(
            {
                'client': strategy_data['client'],
                'klines': strategy_data['klines'],
                'p_precision': strategy_data['p_precision'],
                'q_precision': strategy_data['q_precision'],
            }
        )

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=RuntimeWarning)
            equity = strategy_data['instance'].get_equity(
                strategy_data['instance'].initial_capital,
                strategy_data['instance'].completed_deals_log
            )
            metrics = strategy_data['instance'].get_metrics(
                strategy_data['instance'].initial_capital,
                strategy_data['instance'].completed_deals_log
            )

        return equity, metrics