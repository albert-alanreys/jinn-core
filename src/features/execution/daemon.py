from logging import getLogger
from threading import Thread
from time import sleep
from weakref import WeakKeyDictionary

from src.core.providers import RealtimeProvider
from src.infrastructure.messaging import TelegramClient
from .tester import StrategyTester


class ExecutionDaemon():
    def __init__(self) -> None:
        self.contexts_weak_map = WeakKeyDictionary()
        self.realtime_provider = RealtimeProvider()
        self.telegram_client = TelegramClient()
        self.strategy_tester = StrategyTester()
        self.logger = getLogger(__name__)

        self.strategy_alerts = {}

        Thread(target=self._run, daemon=True).start()

    def add_contexts(self, contexts: dict) -> None:
        for cid, context in contexts.items():
            try:
                if context['is_live']:
                    self.contexts_weak_map[cid] = context
            except Exception:
                self.logger.exception('An error occurred')
                contexts[cid].update({'status': 'failed'})

    def _run(self) -> None:
        while True:
            for cid, context in self.contexts_weak_map.items():
                try:
                    if self.realtime_provider.update_data(context):
                        self._execute_strategy(cid)
                        self._process_alerts(cid)
                except Exception:
                    self.logger.exception('An error occurred')

            sleep(1.0)

    def _execute_strategy(self, context: dict) -> None:
        strategy = context['strategy']
        strategy.calculate(context['market_data'])
        strategy.trade(context['client'])
        self.strategy_tester.test(context)

    def _process_alerts(self, context_id: str) -> None:
        context = self.contexts_weak_map[context_id]
        alerts = context['client'].trade.alerts

        for alert in alerts:
            strategy_name = '-'.join(
                word.capitalize() for word in context['name'].split('_')
            )
            alert_content = {
                'contextId': context_id,
                'strategy': strategy_name,
                **alert
            }

            self.strategy_alerts[str(id(alert_content))] = alert_content
            self.telegram_client.send_order_alert(alert)

        alerts.clear()