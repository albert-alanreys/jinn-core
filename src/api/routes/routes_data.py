from ast import literal_eval
from json import dumps

from flask import request

from src.api.formatting import Formatter
from src.services.testing import Tester


def register_data_routes(app):
    @app.route('/data/alerts', methods=['GET'])
    def get_alerts():
        return dumps(app.strategy_alerts)

    @app.route('/data/summary', methods=['GET'])
    def get_summary():
        summary = Formatter.format_summary(app.strategy_contexts)
        return dumps(summary)

    @app.route('/data/updates', methods=['GET'])
    def get_updates():
        return dumps(app.data_updates)

    @app.route('/data/details/<string:context_id>', methods=['GET'])
    def get_details(context_id):
        context = app.strategy_contexts[context_id]
        context['stats'] = Tester.test(context)
        details = Formatter.format_details(context)

        if context_id in app.data_updates:
            app.data_updates.remove(context_id)

        return dumps(details)

    @app.route('/data/update/<string:context_id>', methods=['PATCH'])
    def update_data(context_id):
        try:
            data = request.get_json()
            param = data.get('param')
            raw_value = data.get('value')

            instance = app.strategy_contexts[context_id]['instance']
            params = instance.params

            old_value = params[param]
            new_value = _parse_value(raw_value)

            if type(old_value) != type(new_value):
                raise TypeError()

            params[param] = new_value
            instance = app.strategy_contexts[context_id]['type'](
                client=app.strategy_contexts[context_id]['client'],
                all_params=params
            )
            app.strategy_contexts[context_id]['instance'] = instance
            return dumps({'status': 'success'}), 200
        except ValueError:
            return dumps({'status': 'error', 'type': 'invalid_request'}), 400
        except TypeError:
            return dumps({'status': 'error', 'type': 'invalid_type'}), 400
        except Exception:
            return dumps({'status': 'error', 'type': 'server_error'}), 500

    def _parse_value(raw):
        if isinstance(raw, list):
            return [float(x) for x in raw]

        if isinstance(raw, str):
            raw = raw.capitalize()

        return literal_eval(raw)