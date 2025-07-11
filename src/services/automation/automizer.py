from logging import getLogger
from threading import Thread
from time import sleep

from src.services.testing.tester import Tester
from .realtime_provider import RealtimeProvider


class Automizer():
    def __init__(self, strategy_contexts: dict) -> None:
        self.strategy_contexts = strategy_contexts

        self.realtime_provider = RealtimeProvider()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        summary = [
            ' | '.join([
                item['name'],
                item['client'].EXCHANGE,
                item['market_data']['symbol'],
                str(item['market_data']['interval'])
            ])
            for item in self.strategy_contexts.values()
        ]
        self.logger.info(f"Automation started for:\n{'\n'.join(summary)}")

        Thread(target=self._automate, daemon=True).start()

    def _automate(self) -> None:
        while True:
            for cid, context in self.strategy_contexts.items():
                try:
                    if self.realtime_provider.update_data(context):
                        self._execute_strategy(cid)
                        context['updated'] = True
                except Exception:
                    self.logger.exception('An error occurred')

            sleep(1.0)

    def _execute_strategy(self, context_id: str) -> None:
        context = self.strategy_contexts[context_id]

        instance = context['instance']
        instance.calculate(context['market_data'])
        instance.trade()

        context['stats'] = Tester.test(instance)