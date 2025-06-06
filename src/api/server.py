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
        strategy_states: dict,
        tester: Optional['Tester']
    ) -> None:
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )
        register_routes(self)

        self.mode = mode
        self.strategy_states = strategy_states

        self.data_formatter = DataFormatter(strategy_states, mode)
        self.strategy_manager = StrategyManager(strategy_states, tester)
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
            for strategy_id, strategy_state in self.strategy_states.items():
                try:
                    if strategy_state['updated']:
                        self.data_formatter.format_strategy_states(
                            strategy_id, strategy_state
                        )
                        self._set_data_updates(strategy_id)
                        strategy_state['updated'] = False

                    if strategy_state['alerts']:
                        self._set_alert_updates(strategy_state['alerts'])
                        strategy_state['alerts'].clear()
                except Exception as e:
                    self.logger.error(f'{type(e).__name__} - {e}')

            sleep(3.0)

    def _set_alert_updates(self, alerts: list) -> None:
        self.alert_updates.extend(alerts)

    def _set_data_updates(self, strategy_id: str) -> None:
        if strategy_id not in self.data_updates:
            self.data_updates.append(strategy_id)