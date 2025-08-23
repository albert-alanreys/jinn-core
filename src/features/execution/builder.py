from logging import getLogger
from typing import TYPE_CHECKING

from src.core.strategies import strategies
from src.infrastructure.exchanges import BinanceClient
from src.infrastructure.exchanges import BybitClient
from src.infrastructure.exchanges.enums import Exchange, Interval
from src.core.providers import HistoryProvider
from src.core.providers import RealtimeProvider
from .tester import StrategyTester

if TYPE_CHECKING:
    from .models import StrategyContext


class ContextBuilder:
    """Builds contexts for trading strategies."""

    def __init__(self) -> None:
        self.history_provider = HistoryProvider()
        self.realtime_provider = RealtimeProvider()
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.strategy_tester = StrategyTester()
        self.logger = getLogger(__name__)

    def build(self, config: dict) -> 'StrategyContext':
        strategy_class = strategies[config['strategy']]
        strategy = strategy_class(config['params'])
        
        match config['exchange']:
            case Exchange.BINANCE.value:
                client = self.binance_client
            case Exchange.BYBIT.value:
                client = self.bybit_client

        is_live = config['is_live']

        if not is_live:
            market_data = self.history_provider.get_market_data(
                client=client,
                symbol=config['symbol'],
                interval=Interval(config['interval']),
                start=config['start'],
                end=config['end'],
                feeds=strategy.params.get('feeds')
            )
        else:
            market_data = self.realtime_provider.get_market_data(
                client=client,
                symbol=config['symbol'],
                interval=Interval(config['interval']),
                feeds=strategy.params.get('feeds')
            )

        metrics = self.strategy_tester.test(strategy)

        return {
            'name': config['strategy'],
            'strategy': strategy,
            'client': client,
            'market_data': market_data,
            'metrics': metrics,
        }