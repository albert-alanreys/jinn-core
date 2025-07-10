from logging import getLogger
from threading import Thread
from time import sleep

from flask import Flask

from src.services.automation.api_clients.telegram import TelegramClient


class StrategyUpdateHandler:
    def __init__(self, strategy_contexts: dict, app: Flask) -> None:
        self.strategy_contexts = strategy_contexts
        self.app = app

        self._running = False
        self.alert_id = 1

        self.telegram_client = TelegramClient()
        self.logger = getLogger(__name__)

    def start(self) -> None:
        if not self._running:
            self._running = True
            Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
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
        if context_id not in self.app.updated_contexts:
            self.app.updated_contexts.append(context_id)