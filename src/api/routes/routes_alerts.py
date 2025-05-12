import json


def register_alert_routes(app):
    @app.route('/updates/alerts')
    def get_alert_updates():
        alerts = app.alert_updates.copy()
        app.alert_updates.clear()
        app.set_alerts(alerts)
        return json.dumps(alerts)

    @app.route('/alerts')
    def get_alerts():
        return json.dumps(app.alerts[-100:])