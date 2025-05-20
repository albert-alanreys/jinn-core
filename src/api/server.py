import threading
from typing import Optional, TYPE_CHECKING

from flask import Flask

from src.core.enums import Mode
from src.core.strategy.strategy_manager import StrategyManager
from src.core.utils.singleton import singleton
from .formatting.data_formatter import DataFormatter
from .routes import register_routes

if TYPE_CHECKING:
    from src.services.testing.tester import Tester


@singleton
class Server(Flask):
    def __init__(
        self,
        import_name: str,
        static_folder: str,
        template_folder: str,
        mode: Mode,
        data_to_format: dict,
        tester: Optional['Tester']
    ) -> None:
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )
        register_routes(self)

        self.mode = mode
        self.data_to_format = data_to_format

        self.formatter = DataFormatter(mode, data_to_format)
        self.manager = StrategyManager(data_to_format, tester)
        self.formatter.format()

        self.alert_updates = []
        self.data_updates = []
        self.alerts = []

        if self.mode is Mode.AUTOMATION:
            thread = threading.Thread(target=self.check_strategies)
            thread.start()

    def set_alerts(self, alerts: list) -> None:
        self.alerts.extend(alerts)

    def set_alert_updates(self, alerts: list) -> None:
        self.alert_updates.extend(alerts)

    def set_data_updates(self, strategy_id: str) -> None:
        if strategy_id not in self.data_updates:
            self.data_updates.append(strategy_id)
    
    def check_strategies(self) -> None:
        while True:
            for strategy_id, strategy_data in self.data_to_format.items():
                if strategy_data['updated']:
                    self.formatter.format_strategy_data(
                        strategy_id, strategy_data
                    )
                    self.set_data_updates(strategy_id)
                    strategy_data['updated'] = False

                if strategy_data['alerts']:
                    self.set_alert_updates(strategy_data['alerts'])
                    strategy_data['alerts'].clear()