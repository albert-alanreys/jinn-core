import threading
import json
import os

from flask import Flask, render_template, Response

from src.controller.preprocessor import Preprocessor


class FlaskApp(Flask):
    def __init__(
        self,
        mode: str,
        strategies: dict[str, dict],
        **args: str
    ) -> None:
        self.mode = mode
        self.strategies = strategies
        self.preprocessor = Preprocessor(self.mode, self.strategies)

        self.data_updates = []
        self.alert_updates = []
        self.alerts = []

        super().__init__(**args)
        self.route('/')(self.index)
        self.route('/mode')(self.get_mode)
        self.route('/updates/alerts')(self.get_alert_updates)
        self.route('/alerts')(self.get_alerts)
        self.route('/updates/data')(self.get_data_updates)
        self.route('/data/lite')(self.get_lite_data)
        self.route('/data/main/<string:id>')(self.get_main_data)
        self.route(
            '/data/update/<string:id>/<string:parameter>', methods=['POST']
        )(self.update_data)

        with open(os.path.abspath('.env'), 'r') as file:
            data = file.read()
            base_url = data[data.rfind('BASE_URL=') + 9 :].rstrip('\n')

        fetch_js_path = os.path.abspath('src/view/static/js/fetchClient.js')

        with open(fetch_js_path, 'r') as file:
            lines = file.readlines()

        old_url = lines[0][lines[0].find('"') + 1 : lines[0].rfind('"')]
        lines[0] = lines[0].replace(old_url, base_url)

        with open(fetch_js_path, 'w') as file:
            file.writelines(lines)

        if self.mode == 'automation':
            self.thread = threading.Thread(target=self.check_strategies)
            self.thread.start()
  
    def set_data_updates(self, id: str) -> None:
        if id not in self.data_updates:
            self.data_updates.append(id)

    def set_alert_updates(self, alerts: list[dict]) -> None:
        self.alert_updates.extend(alerts)

    def set_alerts(self, alerts: list[dict]) -> None:
        self.alerts.extend(alerts)
    
    def index(self) -> Response:
        return render_template('index.html')

    def get_mode(self) -> str:
        return self.mode
    
    def get_alert_updates(self) -> str:
        alerts = self.alert_updates.copy()
        self.alert_updates.clear()
        self.set_alerts(alerts)
        return json.dumps(alerts)

    def get_alerts(self) -> str:
        return json.dumps(self.alerts[-100:])

    def get_data_updates(self) -> str:
        return json.dumps(self.data_updates)

    def get_lite_data(self) -> str:
        return json.dumps(self.preprocessor.lite_data)

    def get_main_data(self, id: str) -> str:
        if id in self.data_updates:
            self.data_updates.remove(id)

        return json.dumps(self.preprocessor.main_data[id])
    
    def update_data(self, id: str, parameter: str) -> tuple[str, int]:
        try:
            parameter_name = list(json.loads(parameter).items())[0][0]
            new_value = list(json.loads(parameter).items())[0][1]
            self.preprocessor.update_strategy(id, parameter_name, new_value)
            response = {"status": "success"}
            http_status = 200
        except ValueError:
            response = {"status": "error"}
            http_status = 400

        return json.dumps(response), http_status
    
    def check_strategies(self) -> None:
        while True:
            for id, data in self.strategies.items():
                if data['updated']:
                    self.preprocessor.prepare_data(id, data)
                    self.set_data_updates(id)
                    data['updated'] = False

                if data['alerts']:
                    self.set_alert_updates(data['alerts'])
                    data['alerts'].clear()