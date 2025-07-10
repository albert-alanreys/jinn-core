import json
import os
from datetime import datetime, timedelta
from logging import getLogger

from src.core.enums import Exchange, Market, Strategy
from src.core.storage.history_provider import HistoryProvider
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient


class OptimizationBuilder:
    def __init__(self, config: dict) -> None:
        self.strategy = config['strategy']
        self.exchange = config['exchange']
        self.market = config['market']
        self.symbol = config['symbol']
        self.interval = config['interval']
        self.start = config['start']
        self.end = config['end']

        self.history_provider = HistoryProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self) -> dict:
        strategy_contexts = {}

        for strategy in Strategy:
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
                    case Exchange.BINANCE.name:
                        client = self.binance_client
                    case Exchange.BYBIT.name:
                        client = self.bybit_client

                match market:
                    case Market.FUTURES.name:
                        market = Market.FUTURES
                    case Market.SPOT.name:
                        market = Market.SPOT

                try:
                    market_data = self._get_market_data(
                        client=client,
                        market=market,
                        symbol=symbol,
                        interval=interval,
                        start=start,
                        end=end,
                        feeds=strategy.value.params.get('feeds')
                    )
                    context = {
                        'name': strategy.name,
                        'type': strategy.value,
                        'client': client,
                        'market_data': market_data
                    }
                    strategy_contexts[str(id(context))] = context
                except Exception:
                    self.logger.exception('An error occurred')

        if not strategy_contexts:
            match self.exchange:
                case Exchange.BINANCE:
                    client = self.binance_client
                case Exchange.BYBIT:
                    client = self.bybit_client

            try:
                market_data = self._get_market_data(
                    client=client,
                    market=self.market,
                    symbol=self.symbol,
                    interval=self.interval,
                    start=self.start,
                    end=self.end,
                    feeds=self.strategy.value.params.get('feeds')
                )
                context = {
                    'name': self.strategy.name,
                    'type': self.strategy.value,
                    'client': client,
                    'market_data': market_data
                }
                strategy_contexts[str(id(context))] = context
            except Exception:
                self.logger.exception('An error occurred')

        return strategy_contexts
    
    def _get_market_data(
        self,
        client: BinanceClient | BybitClient,
        market: Market,
        symbol: str,
        interval: str,
        start: str,
        end: str,
        feeds: list | None
    ) -> dict:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')

        total_days = (end_date - start_date).days
        train_days = int(total_days * 0.7)

        train_end_date = start_date + timedelta(train_days)
        test_start_date = train_end_date + timedelta(1)

        train_data = self.history_provider.fetch_data(
            client=client,
            market=market,
            symbol=symbol,
            interval=interval,
            start=start,
            end=train_end_date.strftime('%Y-%m-%d'),
            feeds=feeds
        )
        test_data = self.history_provider.fetch_data(
            client=client,
            market=market,
            symbol=symbol,
            interval=interval,
            start=test_start_date.strftime('%Y-%m-%d'),
            end=end,
            feeds=feeds
        )

        return {
            'train': train_data,
            'test': test_data
        }