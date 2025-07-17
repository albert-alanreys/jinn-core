from logging import getLogger
from threading import Thread
from time import sleep

from flask import Flask

from src.services.automation.api_clients.telegram import TelegramClient


class StrategyUpdateHandler:
    """
    Background handler that monitors strategy contexts for updates
    and processes generated alerts. Alerts are forwarded to Telegram
    and stored in the application state.

    Automatically runs in a separate daemon thread when started.
    """

    def __init__(self, strategy_contexts: dict, app: Flask) -> None:
        """
        Initializes the StrategyUpdateHandler with the given strategy contexts
        and Flask application instance.

        Prepares internal state for alert tracking, logging,
        and Telegram messaging.

        Args:
            strategy_contexts (dict): Dictionary mapping context IDs
                                      to strategy metadata, including
                                      client instances and update flags
            app (Flask): Flask application instance used for storing
                         and updating shared state
        """

        self.strategy_contexts = strategy_contexts
        self.app = app

        self._running = False
        self.alert_id = 1

        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def start(self) -> None:
        """
        Launches the background thread for monitoring and processing
        strategy updates if it hasn't already been started.
        """

        if not self._running:
            self._running = True
            Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        """
        Background loop that iterates over all strategy contexts,
        checks for updates, and processes any alerts. Executed
        inside a Flask application context.
        """

        with self.app.app_context():
            while self._running:
                for cid, context in self.strategy_contexts.items():
                    try:
                        if context['updated']:
                            alerts = context['client'].alerts

                            if alerts:
                                self._process_alerts(cid, context, alerts)
                                alerts.clear()

                            self._register_context_update(cid)
                            context['updated'] = False
                    except Exception as e:
                        self.logger.error(f'{type(e).__name__}: {str(e)}')

                sleep(5.0)

    def _process_alerts(
        self,
        context_id: str,
        context: dict,
        alerts: list
    ) -> None:
        """
        Processes a list of alerts for a given strategy context:
        - Sends each alert via Telegram
        - Stores alert metadata in the Flask app instance
        - Increments internal alert ID counter

        Args:
            context_id (str): Identifier of the strategy context
            context (dict): Strategy context dictionary
            alerts (list): List of alert dictionaries
        """

        for alert in alerts:
            alert_id = str(self.alert_id)
            strategy_name = '-'.join(
                word.capitalize() for word in context['name'].split('_')
            )
            alert_obj = {
                'context-id': context_id,
                'strategy': strategy_name,
                **alert
            }

            self.telegram_client.send_order_alert(alert)

            self.app.strategy_alerts[alert_id] = alert_obj
            self.app.new_alerts[alert_id] = alert_obj
            self.alert_id += 1

    def _register_context_update(self, context_id: str) -> None:
        """
        Registers a context as updated by appending its ID to
        `app.updated_contexts` if not already present.

        Args:
            context_id (str): Identifier of the updated context
        """

        if context_id not in self.app.updated_contexts:
            self.app.updated_contexts.append(context_id)