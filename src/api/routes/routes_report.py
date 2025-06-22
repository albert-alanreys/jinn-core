from json import dumps
import flask

from src.api.formatting import Formatter
from src.api.utils.error_handling import handle_api_errors


report_bp = flask.Blueprint('report_api', __name__, url_prefix='/api/report')


@report_bp.route('/overview/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_overview(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    overview = Formatter._format_overview(
        completed_deals_log=context['instance'].completed_deals_log,
        equity=context['stats']['equity'],
        metrics=context['stats']['metrics']
    )
    return flask.Response(dumps(overview), mimetype='application/json')


@report_bp.route('/metrics/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_metrics(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    metrics = Formatter._format_metrics(context['stats']['metrics'])
    return flask.Response(dumps(metrics), mimetype='application/json')


@report_bp.route('/trades/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_trades(context_id):
    context = flask.current_app.strategy_contexts[context_id]
    trades = Formatter._format_trades(
        completed_deals_log=context['instance'].completed_deals_log,
        open_deals_log=context['instance'].open_deals_log
    )
    return flask.Response(dumps(trades), mimetype='application/json')