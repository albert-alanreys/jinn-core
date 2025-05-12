import json


def register_data_routes(app):
    @app.route('/updates/data')
    def get_data_updates():
        return json.dumps(app.data_updates)

    @app.route('/data/main/<string:strategy_id>')
    def get_main_data(strategy_id):
        if strategy_id in app.data_updates:
            app.data_updates.remove(strategy_id)

        return json.dumps(app.formatter.main_data[strategy_id])

    @app.route('/data/lite')
    def get_lite_data():
        return json.dumps(app.formatter.lite_data)

    @app.route(
      '/data/update/<string:strategy_id>/<string:parameter>',
      methods=['POST']
    )
    def update_data(strategy_id, parameter):
        try:
            data = json.loads(parameter)
            param, value = list(data.items())[0]

            app.formatter.update_strategy(
                strategy_id=strategy_id,
                parameter_name=param,
                new_value=value
            )

            return json.dumps({'status': 'success'}), 200
        except (ValueError, KeyError):
            return json.dumps({'status': 'error'}), 400