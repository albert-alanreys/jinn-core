from threading import Thread
from time import sleep
from typing import Optional, TYPE_CHECKING

from flask import Flask

from src.core.enums import Mode
from src.core.strategy.strategy_manager import StrategyManager
from .formatting.data_formatter import DataFormatter
from .routes import register_routes

if TYPE_CHECKING:
    from src.services.testing.tester import Tester


class Server(Flask):
    def __init__(
        self,
        import_name: str,
        static_folder: str,
        template_folder: str,
        mode: Mode,
        strategy_contexts: dict,
        tester: Optional['Tester']
    ) -> None:
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )
        register_routes(self)

        self.mode = mode
        self.strategy_contexts = strategy_contexts

        self.data_formatter = DataFormatter(strategy_contexts, mode)
        self.strategy_manager = StrategyManager(strategy_contexts, tester)
        self.data_formatter.format()

        self.alerts = []
        self.alert_updates = []
        self.data_updates = []

        if self.mode is Mode.AUTOMATION:
            Thread(target=self._handle_strategy_updates, daemon=True).start()

    def set_alerts(self, alerts: list) -> None:
        self.alerts.extend(alerts)

    def _handle_strategy_updates(self) -> None:
        while True:
            for context_id, strategy_context in self.strategy_contexts.items():
                try:
                    if strategy_context['updated']:
                        self.data_formatter.format_strategy_states(
                            context_id, strategy_context
                        )
                        self._set_data_updates(context_id)
                        strategy_context['updated'] = False

                    if strategy_context['alerts']:
                        self._set_alert_updates(strategy_context['alerts'])
                        strategy_context['alerts'].clear()
                except Exception as e:
                    self.logger.error(f'{type(e).__name__} - {e}')

            sleep(3.0)

    def _set_alert_updates(self, alerts: list) -> None:
        self.alert_updates.extend(alerts)

    def _set_data_updates(self, context_id: str) -> None:
        if context_id not in self.data_updates:
            self.data_updates.append(context_id)