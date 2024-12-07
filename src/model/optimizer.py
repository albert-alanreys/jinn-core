import logging
import json
import multiprocessing
import os

import numpy as np

import src.model.enums as enums
from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient
from src.model.db_manager import DBManager
from src.model.ga import GA


class Optimizer:
    def __init__(self, optimization_info: dict) -> None:
        self.exchange = optimization_info['exchange']
        self.market = optimization_info['market']
        self.symbol = optimization_info['symbol']
        self.interval = optimization_info['interval']
        self.start = optimization_info['start']
        self.end = optimization_info['end']
        self.strategy = optimization_info['strategy']

        self.binance_client = None
        self.bybit_client = BybitClient()
        self.db_manager = DBManager()

        self.logger = logging.getLogger(__name__)

    def optimize(self) -> None:
        self.strategies = dict()

        for strategy in enums.Strategy:
            path_to_file = os.path.abspath(
                f'src/model/strategies/{strategy.name.lower()}'
                f'/optimization/optimization.json'
            )

            if not os.path.exists(path_to_file):
                continue

            with open(path_to_file, 'r') as file:
                configs = json.load(file)
                
                for config in configs:
                    exchange = config['exchange'].lower()
                    market = config['market'].upper()
                    symbol = config['symbol'].upper()
                    interval = config['interval']
                    start = config['start']
                    end = config['end']

                    if exchange == enums.Exchange.BINANCE.name.lower():
                        client = self.binance_client
                    elif exchange == enums.Exchange.BYBIT.name.lower():
                        client = self.bybit_client

                    rows, _ = self.db_manager.fetch_data(
                        db_name=f'{exchange.capitalize()}.db',
                        table=f'{symbol}_{market}_{interval}',
                        start=start,
                        end=end
                    )
                    klines = np.array(rows)

                    fold_size = len(klines) // 3
                    fold_1 = klines[:fold_size]
                    fold_2 = klines[fold_size : 2 * fold_size]
                    fold_3 = klines[2 * fold_size :]

                    p_precision = client.fetch_price_precision(symbol)
                    q_precision = client.fetch_qty_precision(symbol)

                    strategy_id = (
                        f'{strategy.name.lower()}_'
                        f'{exchange}_'
                        f'{symbol}_'
                        f'{interval} '
                        f'T{start} - {end}'
                    )
                    strategy_data = {
                        'name': strategy.name.lower(),
                        'type': strategy.value,
                        'fold_1': fold_1,
                        'fold_2': fold_2,
                        'fold_3': fold_3,
                        'p_precision': p_precision,
                        'q_precision': q_precision,
                    }
                    self.strategies[strategy_id] = strategy_data

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

            rows, _ = self.db_manager.fetch_data(
                db_name=f'{self.exchange.value.capitalize()}.db',
                table=f'{self.symbol}_{market}_{self.interval.value}',
                start=self.start,
                end=self.end
            )
            klines = np.array(rows)

            fold_size = len(klines) // 3
            fold_1 = klines[:fold_size]
            fold_2 = klines[fold_size : 2 * fold_size]
            fold_3 = klines[2 * fold_size :]

            p_precision = client.fetch_price_precision(self.symbol)
            q_precision = client.fetch_qty_precision(self.symbol)

            strategy_id = (
                f'{self.strategy.name.lower()}_'
                f'{self.exchange.value.lower()}_'
                f'{self.symbol}_'
                f'{self.interval.value} '
                f'T{self.start} - {self.end}'
            )
            strategy_data = {
                'name': self.strategy.name.lower(),
                'type': self.strategy.value,
                'fold_1': fold_1,
                'fold_2': fold_2,
                'fold_3': fold_3,
                'p_precision': p_precision,
                'q_precision': q_precision,
            }
            self.strategies[strategy_id] = strategy_data

        delattr(self, 'db_manager')
        self.logger.info('Optimization process started')

        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            results = zip(
                self.strategies.items(),
                pool.map(
                    self.run_ga,
                    self.strategies.values()
                )
            )

        for strategy, best_samples in results:
            self.write(strategy, best_samples)

    def run_ga(self, strategy: dict) -> dict:
        ga = GA(strategy)
        ga.fit()
        return ga.best_samples

    def write(self, strategy: tuple, best_samples: list) -> None:
        strategy_name = strategy[1]['name']
        time = strategy[0][strategy[0].find(' T') + 2:]
        file_name = (
            strategy[0].
            replace(f'{strategy_name}_', '').
            replace(f' T{time}', '')
        )
        file_path = os.path.abspath(
            f'src/model/strategies/{strategy_name}'
            f'/optimization/{file_name}.txt'
        )

        for sample in best_samples:
            file_text = (
                f'Period: {time}\n'
                f'{"=" * 50}\n'
                + ''.join(
                    f'{param} = {sample[idx]}\n'
                        for idx, param in enumerate(
                            strategy[1]['type'].opt_params.keys()
                        )
                )
                + f'{"=" * 50}\n'
            )

            with open(file_path, 'a') as file:
                print(file_text, file=file)