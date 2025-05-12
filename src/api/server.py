import threading
import os

from flask import Flask

import config
from src.api.formatter import Formatter
from src.core.enums import Mode
from .routes import register_routes


class Server(Flask):
    def __init__(
        self,
        mode: Mode,
        data_to_process: dict,
        import_name: str,
        static_folder: str,
        template_folder: str
    ) -> None:
        self.mode = mode
        self.data_to_process = data_to_process[1]

        self.alerts = []
        self.alert_updates = []
        self.data_updates = []

        self.formatter = Formatter(mode, data_to_process)
        self.formatter.format()

        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )

        register_routes(self)
        self._update_fetch_js_url(config.URL)

        if self.mode is Mode.AUTOMATION:
            thread = threading.Thread(target=self.check_strategies)
            thread.start()

    def _update_fetch_js_url(self, url: str) -> None:
        path_to_fetch_js = os.path.abspath(
            os.path.join('src', 'view', 'static', 'js', 'fetchClient.js')
        )

        with open(path_to_fetch_js, 'r') as file:
            lines = file.readlines()

        old_url = lines[0][lines[0].find('"') + 1 : lines[0].rfind('"')]
        lines[0] = lines[0].replace(old_url, url)

        with open(path_to_fetch_js, 'w') as file:
            file.writelines(lines)

    def set_alerts(self, alerts: list) -> None:
        self.alerts.extend(alerts)

    def set_alert_updates(self, alerts: list) -> None:
        self.alert_updates.extend(alerts)

    def set_data_updates(self, strategy_id: str) -> None:
        if strategy_id not in self.data_updates:
            self.data_updates.append(strategy_id)
    
    def check_strategies(self) -> None:
        while True:
            for strategy_id, strategy_data in self.data_to_process.items():
                if strategy_data['updated']:
                    self.formatter.format_strategy_data(
                        strategy_id, strategy_data
                    )
                    self.set_data_updates(strategy_id)
                    strategy_data['updated'] = False

                if strategy_data['alerts']:
                    self.set_alert_updates(strategy_data['alerts'])
                    strategy_data['alerts'].clear()