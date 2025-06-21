from ast import literal_eval
from json import dumps

import flask

from src.api.formatting import Formatter
from src.services.testing.tester import Tester


api_bp = flask.Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = flask.current_app.strategy_alerts
    return flask.Response(dumps(alerts), mimetype='application/json')


@api_bp.route('/summary', methods=['GET'])
def get_summary():
    summary = Formatter.format_summary(
        flask.current_app.strategy_contexts
    )
    return flask.Response(dumps(summary), mimetype='application/json')


@api_bp.route('/updates', methods=['GET'])
def get_updates():
    updates = flask.current_app.data_updates.copy()
    flask.current_app.data_updates.clear()
    return flask.Response(dumps(updates), mimetype='application/json')


@api_bp.route('/details/chart/<string:context_id>', methods=['GET'])
def get_chart_details(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    chart_details = Formatter.format_chart_details(context)
    return flask.Response(dumps(chart_details), mimetype='application/json')


@api_bp.route('/contexts/<string:context_id>', methods=['PATCH'])
def update_context(context_id):
    try:
        data = flask.request.get_json()
        param = data.get('param')
        raw_value = data.get('value')

        context = flask.current_app.strategy_contexts[context_id]
        instance = context['instance']
        params = instance.params

        old_value = params[param]
        new_value = _parse_value(raw_value)

        if isinstance(old_value, float) and isinstance(new_value, int):
            new_value = float(new_value)
        elif type(old_value) != type(new_value):
            raise TypeError()

        params[param] = new_value
        instance = context['type'](
            client=context['client'],
            all_params=params
        )
        instance.start(context['market_data'])

        context['instance'] = instance
        context['stats'] = Tester.test(instance)

        return flask.Response(
            dumps({'status': 'success'}),
            mimetype='application/json',
            status=200
        )
    except ValueError:
        return flask.Response(
            dumps({'status': 'error', 'type': 'invalid_request'}),
            mimetype='application/json',
            status=400
        )
    except TypeError:
        return flask.Response(
            dumps({'status': 'error', 'type': 'invalid_type'}),
            mimetype='application/json',
            status=400
        )
    except Exception:
        return flask.Response(
            dumps({'status': 'error', 'type': 'server_error'}),
            mimetype='application/json',
            status=500
        )


def _parse_value(raw):
    if isinstance(raw, list):
        return [float(x) for x in raw]

    if isinstance(raw, str):
        raw = raw.capitalize()

    return literal_eval(raw)