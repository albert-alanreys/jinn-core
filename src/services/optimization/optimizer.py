import json
import logging
import multiprocessing
import os

import src.core.enums as enums
from src.core.storage.data_manager import DataManager
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient
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
        self.bybit_client = BybitClient()
        self.logger = logging.getLogger(__name__)

    def optimize(self) -> None:
        for strategy in enums.Strategy:
            path_to_file = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'optimization',
                    'optimization.json'
                )
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

                    if market == enums.Market.FUTURES.name:
                        market = enums.Market.FUTURES
                    elif market == enums.Market.SPOT.name:
                        market = enums.Market.SPOT

                    interval = client.get_valid_interval(interval)

                    try:
                        klines = self.data_manager.get_data(
                            client=client,
                            market=market,
                            symbol=symbol,
                            interval=interval,
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
                            'name': strategy.name.lower(),
                            'exchange': exchange,
                            'market': market.value,
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
                    except Exception as e:
                        self.logger.error(e)

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

            try:
                klines = self.data_manager.get_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.interval,
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
                    'name': self.strategy.name.lower(),
                    'exchange': self.exchange.value,
                    'market': self.market.value,
                    'symbol': self.symbol,
                    'interval': self.interval,
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
            except Exception as e:
                self.logger.error(e)

        strategies_info = [
            ' | '.join([
                item['name'].capitalize(),
                item['exchange'].capitalize(),
                item['market'],
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

        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
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
                f'{strategy['market']}_'
                f'{strategy['interval']}.txt'
            )
            path_to_file = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy['name'],
                    'optimization',
                    filename
                )
            )

            for sample in strategy['best_samples']:
                file_text = (
                    f'Period: {strategy['start']} - {strategy['end']}\n'
                    f'{'=' * 50}\n'
                    + ''.join(
                        f'{param} = {sample[idx]}\n'
                            for idx, param in enumerate(
                                strategy['type'].opt_params.keys()
                            )
                    )
                    + f'{'=' * 50}\n'
                )

                with open(path_to_file, 'a') as file:
                    print(file_text, file=file)