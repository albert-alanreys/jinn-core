import threading

from flask import Flask

from src.core.enums import Mode
from src.core.strategies.strategy_manager import StrategyManager
from .formatting.data_formatter import DataFormatter
from .routes import register_routes


class Server(Flask):
    def __init__(
        self,
        mode: Mode,
        data_to_format: tuple,
        import_name: str,
        static_folder: str,
        template_folder: str
    ) -> None:
        self.mode = mode
        self.data_to_format = data_to_format[1]

        self.alerts = []
        self.alert_updates = []
        self.data_updates = []

        self.formatter = DataFormatter(mode, data_to_format)
        self.manager = StrategyManager(mode, data_to_format)

        self.formatter.format()

        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )
        register_routes(self)

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