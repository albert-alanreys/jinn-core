from json import dumps
import flask

from src.api.formatting import Formatter
from src.api.utils.error_handling import handle_api_errors

chart_bp = flask.Blueprint('chart_api', __name__, url_prefix='/api/chart')


@chart_bp.route('/klines/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_klines(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    klines = Formatter._format_klines(
        context['market_data']['klines']
    )
    return flask.Response(dumps(klines), mimetype='application/json')


@chart_bp.route('/indicators/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_indicators(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    indicators = Formatter._format_indicators(
        context['market_data'],
        context['instance'].indicators
    )
    return flask.Response(dumps(indicators), mimetype='application/json')


@chart_bp.route('/markers/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_markers(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    markers = Formatter._format_markers(
        context['instance'].completed_deals_log,
        context['instance'].open_deals_log
    )
    return flask.Response(dumps(markers), mimetype='application/json')