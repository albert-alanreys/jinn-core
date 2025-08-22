from logging import getLogger

from src.core.strategies import strategies
from src.infrastructure.exchanges import BinanceClient
from src.infrastructure.exchanges import BybitClient
from src.infrastructure.exchanges.enums import Exchange, Interval
from src.core.providers import HistoryProvider
from src.core.providers import RealtimeProvider


class ContextBuilder:
    """Builds contexts for trading strategies."""

    def __init__(self) -> None:
        self.history_provider = HistoryProvider()
        self.realtime_provider = RealtimeProvider()

        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()

        self.logger = getLogger(__name__)

    def build(self, contexts: dict, configs: dict) -> None:
        for cid, config in configs.items():
            try:
                strategy_class = strategies[configs['strategy']]
                strategy = strategy_class(configs['params'])
                
                match configs['client']:
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
                        start=configs['start'],
                        end=configs['end'],
                        feeds=strategy.params.get('feeds')
                    )
                else:
                    market_data = self.realtime_provider.get_market_data(
                        client=client,
                        symbol=config['symbol'],
                        interval=Interval(config['interval']),
                        feeds=strategy.params.get('feeds')
                    )

                context = {
                    'name': configs['strategy'],
                    'strategy': strategy,
                    'client': client,
                    'market_data': market_data
                }
                contexts[cid].update(context)
            except Exception:
                self.logger.exception('An error occurred')
                contexts[cid].update({'status': 'failed'})