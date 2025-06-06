import json
import os
from logging import getLogger
from multiprocessing import Pool, cpu_count

import src.core.enums as enums
from src.core.storage.history_provider import HistoryProvider
from src.services.automation.api_clients.binance import BinanceREST
from src.services.automation.api_clients.bybit import BybitREST
from src.services.automation.api_clients.telegram import TelegramClient
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

        self.history_provider = HistoryProvider()
        self.telegram_client = TelegramClient()
        self.binance_client = BinanceREST(self.telegram_client)
        self.bybit_client = BybitREST(self.telegram_client)

        self.strategy_states = {}

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

                try:
                    feeds = strategy.value.params.get('feeds')
                    market_data = self.history_provider.fetch_data(
                        client=client,
                        market=market,
                        symbol=symbol,
                        interval=interval,
                        start=start,
                        end=end,
                        extra_feeds=feeds
                    )

                    total_len = len(market_data['klines'])
                    train_size = int(total_len * 0.7)

                    train_data = market_data['klines'][:train_size]
                    test_data = market_data['klines'][train_size:]

                    strategy_state = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'client': client,
                        'market_data': market_data,
                        'train_data': train_data,
                        'test_data': test_data
                    }
                    strategy_id = str(id(strategy_state))
                    self.strategy_states[strategy_id] = strategy_state
                except Exception:
                    self.logger.exception('An error occurred')

        if not self.strategy_states:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = self.binance_client
                case enums.Exchange.BYBIT:
                    client = self.bybit_client

            try:
                feeds = self.strategy.value.params.get('feeds')
                market_data = self.history_provider.fetch_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.interval,
                    start=self.start,
                    end=self.end,
                    extra_feeds=feeds
                )

                total_len = len(market_data['klines'])
                train_size = int(total_len * 0.7)

                train_data = market_data['klines'][:train_size]
                test_data = market_data['klines'][train_size:]

                strategy_state = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'client': client,
                    'market_data': market_data,
                    'train_data': train_data,
                    'test_data': test_data
                }
                strategy_id = str(id(strategy_state))
                self.strategy_states[strategy_id] = strategy_state
            except Exception:
                self.logger.exception('An error occurred')

        strategies_info = [
            ' | '.join([
                item['name'],
                item['client'].EXCHANGE,
                item['market_data']['market'].value,
                item['market_data']['symbol'],
                str(item['market_data']['interval']),
                f"{item['market_data']['start']} → "
                f"{item['market_data']['end']}"
            ])
            for item in self.strategy_states.values()
        ]
        self.logger.info(
            'Optimization started for:\n' +
            '\n'.join(strategies_info)
        )
        self.telegram_client.send_message('🔥 Оптимизация началась')

        with Pool(cpu_count()) as p:
            if hasattr(self, 'history_provider'):
                delattr(self, 'history_provider')

            best_samples_list = p.map(
                func=self._run_optimization,
                iterable=self.strategy_states.values()
            )

        for key, samples in zip(self.strategy_states, best_samples_list):
            self.strategy_states[key]['best_samples'] = samples

        self._save_params()

        self.logger.info('Optimization completed')
        self.telegram_client.send_message('✅ Оптимизация завершена')

    def _run_optimization(self, strategy_state: dict) -> list:
        ga = GA(strategy_state)
        ga.fit()
        return ga.best_samples

    def _save_params(self) -> None:
        for strategy in self.strategy_states.values():
            filename = (
                f'{strategy['client'].EXCHANGE}_'
                f'{strategy['market_data']['market'].value}_'
                f'{strategy['market_data']['symbol']}_'
                f'{strategy['market_data']['interval']}.json'
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
                        'start': strategy['market_data']['start'],
                        'end': strategy['market_data']['end']
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