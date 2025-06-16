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

        self.strategy_alerts = []
        self.data_updates = []

        if self.mode is Mode.AUTOMATION:
            Thread(target=self._handle_strategy_updates, daemon=True).start()

    def _handle_strategy_updates(self) -> None:
        while True:
            for cid, context in self.strategy_contexts.items():
                try:
                    if context['updated']:
                        alerts = context['client'].alerts

                        if alerts:
                            self.strategy_alerts.extend(
                                {'cid': cid, **alert}
                                for alert in alerts
                            )
                            alerts.clear()

                        self._set_data_updates(cid)
                        context['updated'] = False
                except Exception as e:
                    self.logger.error(f'{type(e).__name__} - {e}')

            sleep(5.0)

    def _set_data_updates(self, context_id: str) -> None:
        if context_id not in self.data_updates:
            self.data_updates.append(context_id)