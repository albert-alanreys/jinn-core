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

        return json.dumps(app.data_formatter.main_data[strategy_id])

    @app.route('/data/lite')
    def get_lite_data():
        return json.dumps(app.data_formatter.lite_data)

    @app.route('/data/update/<string:strategy_id>', methods=['PATCH'])
    def update_data(strategy_id):
        try:
            data = request.get_json()
            param = data.get('param')
            value = data.get('value')

            app.strategy_manager.update_strategy(
                strategy_id=strategy_id,
                param_name=param,
                new_value=value
            )
            app.data_formatter.format_strategy_states(
                strategy_id=strategy_id,
                strategy_state=app.strategy_states[strategy_id]
            )
            return json.dumps({'status': 'success'}), 200
        except ValueError:
            return json.dumps({
                'status': 'error',
                'type': 'invalid_request'
            }), 400
        except KeyError:
            return json.dumps({
                'status': 'error',
                'type': 'not_found'
            }), 400
        except TypeError:
            return json.dumps({
                'status': 'error',
                'type': 'invalid_type'
            }), 400
        except Exception:
            return json.dumps({
                'status': 'error',
                'type': 'server_error'
            }), 500