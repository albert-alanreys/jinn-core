import glob
import json
import logging
import os
import re
import warnings

import src.core.enums as enums
from src.core.storage.data_manager import DataManager
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient
from .performance_metrics import get_performance_metrics


class Tester:
    def __init__(self, testing_info: dict) -> None:
        self.exchange = testing_info['exchange']
        self.market = testing_info['market']
        self.symbol = testing_info['symbol']
        self.interval = testing_info['interval']
        self.start = testing_info['start']
        self.end = testing_info['end']
        self.strategy = testing_info['strategy']

        self.strategies = {}
        self.data_manager = DataManager()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.logger = logging.getLogger(__name__)

    def test(self) -> None:
        self.logger.info('Testing process started')

        for strategy in enums.Strategy:
            folder_path = os.path.abspath(
                os.path.join(
                    'src',
                    'strategies',
                    strategy.name.lower(),
                    'backtesting'
                )
            )
            file_paths = glob.glob(f'{folder_path}/*.json')

            for file_path in file_paths:
                basename = os.path.basename(file_path) 
                pattern = r'(\w+)_(\w+)_(\w+)_(\w+)\.json'
                groups = re.match(pattern, basename).groups()
                exchange, symbol, market, interval = (
                    groups[0].upper(),
                    groups[1].upper(),
                    groups[2].upper(),
                    groups[3]
                )

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

                with open(file_path, 'r') as file:
                    try:
                        params_dicts = json.load(file)
                    except json.JSONDecodeError:
                        self.logger.error(f'Failed to parse JSON {file_path}')
                        continue

                for params in params_dicts:
                    valid_interval = client.get_valid_interval(interval)

                    try:
                        klines = self.data_manager.get_data(
                            client=client,
                            market=market,
                            symbol=symbol,
                            interval=valid_interval,
                            start=params['period']['start'],
                            end=params['period']['end']
                        )
                        p_precision = client.get_price_precision(symbol)
                        q_precision = client.get_qty_precision(symbol)
                        instance = strategy.value(
                            opt_params=params['params'].values()
                        )

                        strategy_data = {
                            'name': strategy.name,
                            'type': strategy.value,
                            'instance': instance,
                            'params': instance.params,
                            'client': client,
                            'exchange': exchange,
                            'market': market,
                            'symbol': symbol,
                            'interval': valid_interval,
                            'klines': klines,
                            'p_precision': p_precision,
                            'q_precision': q_precision,
                        }

                        equity, metrics = (
                            self.calculate_strategy(strategy_data)
                        )
                        strategy_data['equity'] = equity
                        strategy_data['metrics'] = metrics
                        self.strategies[str(id(strategy_data))] = strategy_data
                    except Exception as e:
                        self.logger.error(f'{type(e).__name__} - {e}')

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
                instance = self.strategy.value()

                strategy_data = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'instance': instance,
                    'params': instance.params,
                    'client': client,
                    'exchange': self.exchange.value,
                    'market': self.market,
                    'symbol': self.symbol,
                    'interval': self.valid_interval,
                    'klines': klines,
                    'p_precision': p_precision,
                    'q_precision': q_precision,
                }

                equity, metrics = self.calculate_strategy(strategy_data)
                strategy_data['equity'] = equity
                strategy_data['metrics'] = metrics
                self.strategies[str(id(strategy_data))] = strategy_data
            except Exception as e:
                self.logger.error(f'{type(e).__name__} - {e}')

    def calculate_strategy(self, strategy_data: dict) -> tuple:
        market_data = {
            'market': strategy_data['market'],
            'symbol': strategy_data['symbol'],
            'klines': strategy_data['klines'],
            'p_precision': strategy_data['p_precision'],
            'q_precision': strategy_data['q_precision']
        }
        strategy_data['instance'].start(
            client=strategy_data['client'],
            market_data=market_data
        )

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=RuntimeWarning)
            equity, metrics = get_performance_metrics(
                strategy_data['instance'].params['initial_capital'],
                strategy_data['instance'].completed_deals_log
            )

        return equity, metrics