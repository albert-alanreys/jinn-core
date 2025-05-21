import json
import os
from logging import getLogger
from multiprocessing import Pool, cpu_count

import src.core.enums as enums
from src.core.storage.data_manager import DataManager
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitREST
from .ga import GA


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
        self.data_manager = DataManager()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitREST()

        self.logger = getLogger(__name__)

    def optimize(self) -> None:
        for strategy in enums.Strategy:
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'optimization',
                    'optimization.json'
                )
            )

            if not os.path.exists(file_path):
                continue

            with open(file_path, 'r') as file:
                try:
                    configs = json.load(file)
                except json.JSONDecodeError:
                    self.logger.error(f'Failed to load JSON from {file_path}')
                    continue

            for config in configs:
                exchange = config['exchange'].upper()
                market = config['market'].upper()
                symbol = config['symbol'].upper()
                interval = config['interval']
                start = config['start']
                end = config['end']

                match exchange:
                    case enums.Exchange.BINANCE.name:
                        client = self.binance_client
                    case enums.Exchange.BYBIT.name:
                        client = self.bybit_client

                match market:
                    case enums.Market.FUTURES.name:
                        market = enums.Market.FUTURES
                    case enums.Market.SPOT.name:
                        market = enums.Market.SPOT

                valid_interval = client.get_valid_interval(interval)

                try:
                    klines = self.data_manager.get_data(
                        client=client,
                        market=market,
                        symbol=symbol,
                        interval=valid_interval,
                        start=start,
                        end=end
                    )
                    p_precision = client.get_price_precision(symbol)
                    q_precision = client.get_qty_precision(symbol)

                    fold_size = len(klines) // 3
                    fold_1 = klines[:fold_size]
                    fold_2 = klines[fold_size : 2 * fold_size]
                    fold_3 = klines[2 * fold_size :]

                    strategy_data = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'client': client,
                        'exchange': exchange,
                        'market': market,
                        'symbol': symbol,
                        'interval': valid_interval,
                        'start': start,
                        'end': end,
                        'fold_1': fold_1,
                        'fold_2': fold_2,
                        'fold_3': fold_3,
                        'p_precision': p_precision,
                        'q_precision': q_precision,
                    }
                    strategy_id = str(id(strategy_data))
                    self.strategies[strategy_id] = strategy_data
                except Exception as e:
                    self.logger.error(
                        msg=f'{type(e).__name__} - {e}',
                        exc_info=True
                    )

        if len(self.strategies) == 0:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            self.valid_interval = client.get_valid_interval(self.interval)

            try:
                klines = self.data_manager.get_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.valid_interval,
                    start=self.start,
                    end=self.end
                )
                p_precision = client.get_price_precision(self.symbol)
                q_precision = client.get_qty_precision(self.symbol)

                fold_size = len(klines) // 3
                fold_1 = klines[:fold_size]
                fold_2 = klines[fold_size : 2 * fold_size]
                fold_3 = klines[2 * fold_size :]

                strategy_data = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'client': client,
                    'exchange': self.exchange.value,
                    'market': self.market,
                    'symbol': self.symbol,
                    'interval': self.valid_interval,
                    'start': self.start,
                    'end': self.end,
                    'fold_1': fold_1,
                    'fold_2': fold_2,
                    'fold_3': fold_3,
                    'p_precision': p_precision,
                    'q_precision': q_precision,
                }
                strategy_id = str(id(strategy_data))
                self.strategies[strategy_id] = strategy_data
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}', exc_info=True)

        strategies_info = [
            ' | '.join([
                item['name'],
                item['exchange'],
                item['market'].value,
                item['symbol'],
                str(item['interval']),
                f"{item['start']} → {item['end']}"
            ])
            for item in self.strategies.values()
        ]
        self.logger.info(
            'Optimization started for:\n' +
            '\n'.join(strategies_info)
        )

        with Pool(cpu_count()) as p:
            if hasattr(self, 'data_manager'):
                delattr(self, 'data_manager')

            best_samples_list = p.map(
                func=self._run_optimization,
                iterable=self.strategies.values()
            )

        for key, samples in zip(self.strategies, best_samples_list):
            self.strategies[key]['best_samples'] = samples

        self._save_params()

    def _run_optimization(self, strategy_data: dict) -> list:
        ga = GA(strategy_data)
        ga.fit()
        return ga.best_samples

    def _save_params(self) -> None:
        for strategy in self.strategies.values():
            filename = (
                f'{strategy['exchange']}_'
                f'{strategy['symbol']}_'
                f'{strategy['market'].value}_'
                f'{strategy['interval']}.json'
            )
            file_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy['name'].lower(),
                    'optimization',
                    filename
                )
            )

            new_items = [
                {
                    'period': {
                        'start': strategy['start'],
                        'end': strategy['end']
                    },
                    'params': dict(
                        zip(strategy['type'].opt_params.keys(), sample)
                    )
                }
                for sample in strategy['best_samples']
            ]
            existing_items = []

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        existing_items = json.load(file)
                    except json.JSONDecodeError:
                        pass

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(existing_items + new_items, file, indent=4)