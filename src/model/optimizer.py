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

        self.strategies = {}
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.db_manager = DBManager()
        self.logger = logging.getLogger(__name__)

    def optimize(self) -> None:
        self.logger.info('Optimization process started')

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
                        db_name=f'{exchange.lower()}.db',
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

                    strategy_data = {
                        'name': strategy.name.lower(),
                        'exchange': exchange,
                        'market': market,
                        'symbol': symbol,
                        'interval': interval,
                        'start': start,
                        'end': end,
                        'type': strategy.value,
                        'fold_1': fold_1,
                        'fold_2': fold_2,
                        'fold_3': fold_3,
                        'p_precision': p_precision,
                        'q_precision': q_precision,
                    }
                    self.strategies[id(strategy_data)] = strategy_data

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
                db_name=f'{self.exchange.value.lower()}.db',
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

            strategy_data = {
                'name': self.strategy.name.lower(),
                'exchange': self.exchange.value.lower(),
                'market': self.market.value,
                'symbol': self.symbol,
                'interval': self.interval.value,
                'start': self.start,
                'end': self.end,
                'type': self.strategy.value,
                'fold_1': fold_1,
                'fold_2': fold_2,
                'fold_3': fold_3,
                'p_precision': p_precision,
                'q_precision': q_precision,
            }
            self.strategies[id(strategy_data)] = strategy_data

        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            delattr(self, 'db_manager')
            best_samples_list = p.map(self.run_ga, self.strategies.values())

        for key, samples in zip(self.strategies, best_samples_list):
            self.strategies[key]['best_samples'] = samples

        self.save_params()

    def run_ga(self, strategy_data: dict) -> list:
        ga = GA(strategy_data)
        ga.fit()
        return ga.best_samples

    def save_params(self) -> None:
        for strategy in self.strategies.values():
            filename = (
                f'{strategy['exchange']}_'
                f'{strategy['symbol']}_'
                f'{strategy['market']}_'
                f'{strategy['interval']}.txt'
            )
            path_to_file = os.path.abspath(
                f'src/model/strategies/{strategy['name']}'
                f'/optimization/{filename}'
            )

            for sample in strategy['best_samples']:
                file_text = (
                    f'Period: {strategy['start']} - {strategy['end']}\n'
                    f'{"=" * 50}\n'
                    + ''.join(
                        f'{param} = {sample[idx]}\n'
                            for idx, param in enumerate(
                                strategy['type'].opt_params.keys()
                            )
                    )
                    + f'{"=" * 50}\n'
                )

                with open(path_to_file, 'a') as file:
                    print(file_text, file=file)