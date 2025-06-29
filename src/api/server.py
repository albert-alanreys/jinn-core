from threading import Thread
from time import sleep

from flask import Flask
from flask_cors import CORS

from src.core.enums import Mode
from .routes import register_routes


class Server(Flask):
    def __init__(
        self,
        import_name: str,
        static_folder: str,
        template_folder: str,
        strategy_contexts: dict,
        mode: Mode
    ) -> None:
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )

        register_routes(self)

        CORS(
            self,
            resources={
                r'/api/*': {
                    'origins': 'http://localhost:5173'
                }
            }
        )

        self.strategy_contexts = strategy_contexts
        self.mode = mode

        self.updated_contexts = []
        self.strategy_alerts = {}
        self.new_alerts = {}
        self.alert_id = 1

        if self.mode is Mode.AUTOMATION:
            Thread(target=self._handle_strategy_updates, daemon=True).start()

    def _handle_strategy_updates(self) -> None:
        while True:
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
                    self.logger.error(f'{type(e).__name__} - {e}')

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
                word.capitalize()
                for word in context['name'].split('_')
            )
            alert_obj = {
                'context-id': context_id,
                'strategy': strategy_name,
                **alert
            }

            self.strategy_alerts[alert_id] = alert_obj
            self.new_alerts[alert_id] = alert_obj
            self.alert_id += 1

    def _register_context_update(self, context_id: str) -> None:
        if context_id not in self.updated_contexts:
            self.updated_contexts.append(context_id)