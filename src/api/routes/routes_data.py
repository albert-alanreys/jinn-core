import json

from flask import request


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

    @app.route('/data/update/<string:strategy_id>', methods=['PATCH'])
    def update_data(strategy_id):
        try:
            data = request.get_json()
            param = data.get('param')
            value = data.get('value')

            app.manager.update_strategy(
                strategy_id=strategy_id,
                param_name=param,
                new_value=value
            )
            app.formatter.format_strategy_data(
                strategy_id=strategy_id,
                strategy_data=app.data_to_format[strategy_id]
            )
            return json.dumps({'status': 'success'}), 200
        except (ValueError, KeyError, TypeError):
            return json.dumps({'status': 'error'}), 400