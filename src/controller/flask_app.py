import threading
import json
import os

from flask import Flask, render_template, Response

import config
from src.controller.preprocessor import Preprocessor
from src.core.enums import Mode


class FlaskApp(Flask):
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

        self.data_updates = []
        self.alert_updates = []
        self.alerts = []

        self.preprocessor = Preprocessor(mode, data_to_process)
        self.preprocessor.process()

        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            template_folder=template_folder
        )

        self.add_url_rule(
            rule='/',
            view_func=self.index
        )
        self.add_url_rule(
            rule='/mode',
            view_func=self.get_mode
        )
        self.add_url_rule(
            rule='/updates/alerts',
            view_func=self.get_alert_updates
        )
        self.add_url_rule(
            rule='/alerts',
            view_func=self.get_alerts
        )
        self.add_url_rule(
            rule='/updates/data',
            view_func=self.get_data_updates
        )
        self.add_url_rule(
            rule='/data/main/<string:strategy_id>',
            view_func=self.get_main_data
        )
        self.add_url_rule(
            rule='/data/lite',
            view_func=self.get_lite_data
        )
        self.add_url_rule(
            rule='/data/update/<string:strategy_id>/<string:parameter>',
            view_func=self.update_data, 
            methods=['POST']
        )

        url = config.URL
        path_to_fetch_js = os.path.abspath(
            os.path.join('src', 'view', 'static', 'js', 'fetchClient.js')
        )

        with open(path_to_fetch_js, 'r') as file:
            lines = file.readlines()

        old_url = lines[0][lines[0].find('"') + 1 : lines[0].rfind('"')]
        lines[0] = lines[0].replace(old_url, url)

        with open(path_to_fetch_js, 'w') as file:
            file.writelines(lines)

        if self.mode is Mode.AUTOMATION:
            thread = threading.Thread(target=self.check_strategies)
            thread.start()
  
    def set_data_updates(self, strategy_id: str) -> None:
        if strategy_id not in self.data_updates:
            self.data_updates.append(strategy_id)

    def set_alert_updates(self, alerts: list) -> None:
        self.alert_updates.extend(alerts)

    def set_alerts(self, alerts: list) -> None:
        self.alerts.extend(alerts)
    
    def index(self) -> Response:
        return render_template('index.html')

    def get_mode(self) -> str:
        return self.mode.value
    
    def get_alert_updates(self) -> str:
        alerts = self.alert_updates.copy()
        self.alert_updates.clear()
        self.set_alerts(alerts)
        return json.dumps(alerts)

    def get_alerts(self) -> str:
        return json.dumps(self.alerts[-100:])

    def get_data_updates(self) -> str:
        return json.dumps(self.data_updates)

    def get_main_data(self, strategy_id: str) -> str:
        if strategy_id in self.data_updates:
            self.data_updates.remove(strategy_id)

        return json.dumps(self.preprocessor.main_data[strategy_id])
    
    def get_lite_data(self) -> str:
        return json.dumps(self.preprocessor.lite_data)

    def update_data(self, strategy_id: str, parameter: str) -> tuple:
        try:
            param = list(json.loads(parameter).items())[0][0]
            value = list(json.loads(parameter).items())[0][1]

            self.preprocessor.update_strategy(
                strategy_id=strategy_id,
                parameter_name=param,
                new_value=value
            )

            response = {"status": "success"}
            http_status = 200
        except (ValueError, KeyError):
            response = {"status": "error"}
            http_status = 400

        return json.dumps(response), http_status
    
    def check_strategies(self) -> None:
        while True:
            for strategy_id, strategy_data in self.data_to_process.items():
                if strategy_data['updated']:
                    self.preprocessor.prepare_strategy_data(
                        strategy_id, strategy_data
                    )
                    self.set_data_updates(strategy_id)
                    strategy_data['updated'] = False

                if strategy_data['alerts']:
                    self.set_alert_updates(strategy_data['alerts'])
                    strategy_data['alerts'].clear()