import json
import os

from flask import Flask, render_template

class FlaskApp(Flask):
    def __init__(self, mode, update_strategy, **args):
        self.mode = mode
        self.update_strategy = update_strategy
        self.data_updates = []
        self.alert_updates = []
        self.alerts = []

        super().__init__(**args)
        self.route('/')(self.index)
        self.route('/mode')(self.get_mode)
        self.route('/alerts')(self.get_alerts)
        self.route('/updates/alerts')(self.get_alert_updates)
        self.route('/updates/data')(self.get_data_updates)
        self.route('/data/lite')(self.get_lite_data)
        self.route('/data/main/<string:id>')(self.get_main_data)
        self.route(
            '/data/update/<string:id>/<string:parameter>', methods=['POST']
        )(self.update_data)

        with open(os.path.abspath('.env'), 'r') as file:
            data = file.read()
            base_url = data[data.rfind('BASE_URL=') + 9 :]

        with open(
            os.path.abspath('src/frontend/static/js/fetchClient.js'), 'r'
        ) as file:
            lines = file.readlines()

        old_url = lines[0][lines[0].find('"') + 1 : lines[0].rfind('"')]
        lines[0] = lines[0].replace(old_url, base_url)

        with open(
            os.path.abspath('src/frontend/static/js/fetchClient.js'), 'w'
        ) as file:
            file.writelines(lines)
  
    def set_data_updates(self, id):
        if id not in self.data_updates:
            self.data_updates.append(id)

    def set_alert_updates(self, alerts):
        self.alert_updates.extend(alerts)

    def set_lite_data(self, lite_data):
        self.lite_data = lite_data

    def set_main_data(self, main_data):
        self.main_data = main_data

    def set_alerts(self, alerts):
        self.alerts.extend(alerts)
    
    def index(self):
        return render_template('index.html')

    def get_mode(self):
        return self.mode
    
    def get_alerts(self):
        return json.dumps(self.alerts[-100:])
    
    def get_alert_updates(self):
        alerts = self.alert_updates.copy()
        self.alert_updates.clear()
        self.set_alerts(alerts)
        return json.dumps(alerts)

    def get_data_updates(self):
        return json.dumps(self.data_updates)

    def get_lite_data(self):
        return json.dumps(self.lite_data)

    def get_main_data(self, id):
        if id in self.data_updates:
            self.data_updates.remove(id)

        return json.dumps(self.main_data[id])
    
    def update_data(self, id, parameter):
        try:
            name = list(json.loads(parameter).items())[0][0]
            new_value = list(json.loads(parameter).items())[0][1]
            self.update_strategy(id, name, new_value)
            response = {"status": "success"}
            http_status = 200
        except:
            response = {"status": "error"}
            http_status = 500

        return json.dumps(response), http_status