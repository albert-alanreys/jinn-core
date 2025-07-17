from logging import getLogger
from threading import Thread
from time import sleep

from src.features.backtesting import BacktestingService
from src.infrastructure.providers import RealtimeProvider


class AutomationService():
    """
    Automates trading strategies execution in real-time.

    Manages continuous execution of trading strategies by monitoring
    market data updates and triggering strategy calculations and trades.
    Runs in a separate daemon thread to avoid blocking the main application.

    Args:
        strategy_contexts (dict): Dictionary of strategy contexts to automate,
                                  prepared by AutomationBuilder
    """

    def __init__(self, strategy_contexts: dict) -> None:
        """
        Initialize AutomationService with strategy contexts.

        Sets up strategy contexts, realtime data provider, and logger.

        Args:
            strategy_contexts (dict): Prepared strategy contexts with
                                      instances, clients, and market data
        """

        self.strategy_contexts = strategy_contexts

        self.realtime_provider = RealtimeProvider()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        """
        Start the automation process.

        Logs summary of strategies being automated and launches
        the automation thread.
        """

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
        """
        Continuous automation loop (runs in background thread).

        Periodically checks for market data updates and executes
        strategies when new data is available. Runs indefinitely
        with 1-second intervals between checks.
        """

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
        """
        Execute a single strategy's calculations and trades.

        Args:
            context_id (str): ID of the strategy context to execute

        Updates strategy statistics after execution using BacktestingService.
        """

        context = self.strategy_contexts[context_id]

        instance = context['instance']
        instance.calculate(context['market_data'])
        instance.trade()

        context['stats'] = BacktestingService.test(instance)