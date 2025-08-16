from logging import getLogger
from threading import Thread
from time import sleep

from src.features.backtesting import BacktestingService
from src.infrastructure.providers import RealtimeProvider
from src.infrastructure.clients.messaging.telegram import TelegramClient


class AutomationService():
    """
    Core service responsible for executing
    trading strategies in real time.

    Core automation service for real-time trading strategy execution.

    Manages continuous execution of trading strategies by monitoring
    market data updates and triggering strategy calculations and trades.
    Runs in a separate daemon thread to avoid blocking the main application.
    """

    def __init__(
        self,
        strategy_contexts: dict,
        strategy_alerts: dict
    ) -> None:
        """
        Initialize AutomationService with strategy contexts.

        Sets up strategy contexts, realtime data provider, and logger.

        Args:
            strategy_contexts (dict): Dictionary of strategy contexts
            strategy_alerts (dict): Dictionary of strategy alerts
        """

        self.strategy_contexts = strategy_contexts
        self.strategy_alerts = strategy_alerts

        self.realtime_provider = RealtimeProvider()
        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def run(self) -> None:
        """
        Start the automation process.

        Logs summary of strategies being automated
        and launches the automation thread.
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

        Periodically iterates through all strategy contexts, checks for
        market data updates, executes strategies when new data
        is available, and processes alerts for each context.
        """

        while True:
            for cid, context in self.strategy_contexts.items():
                try:
                    if self.realtime_provider.update_data(context):
                        self._execute_strategy(cid)
                        self._process_alerts(cid)
                except Exception:
                    self.logger.exception('An error occurred')

            sleep(1.0)

    def _execute_strategy(self, context_id: str) -> None:
        """
        Execute a single strategy's calculations and trades.

        Args:
            context_id (str): ID of the strategy context

        Updates strategy statistics after execution using BacktestingService.
        """

        context = self.strategy_contexts[context_id]

        instance = context['instance']
        instance.calculate(context['market_data'])
        instance.trade()

        context['metrics'] = BacktestingService.test(instance)

    def _process_alerts(self, context_id: str) -> None:
        """
        Processes a list of alerts for a strategy context.
        Sends each alert via Telegram.

        Args:
            context_id (str): ID of the strategy context
        """

        context = self.strategy_contexts[context_id]
        alerts = context['client'].alerts

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