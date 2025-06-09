from json import dumps


def register_alert_routes(app):
    @app.route('/updates/alerts', methods=['GET'])
    def get_alert_updates():
        alerts = app.alert_updates.copy()
        app.alert_updates.clear()
        app.set_alerts(alerts)
        return dumps(alerts)

    @app.route('/alerts', methods=['GET'])
    def get_alerts():
        return dumps(app.strategy_alerts[-100:])