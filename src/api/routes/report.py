from json import dumps
import flask

from src.api.formatting import Formatter
from src.api.utils.error_handling import handle_api_errors


report_bp = flask.Blueprint(
    name='report_api',
    import_name=__name__,
    url_prefix='/api/report'
)


@report_bp.route('/overview/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_overview(context_id):
    """
    Get overview report data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context.

    Returns:
        Response: JSON response containing formatted overview data.
    """

    context = flask.current_app.strategy_contexts[context_id]
    overview = Formatter._format_overview(
        completed_deals_log=context['instance'].completed_deals_log,
        equity=context['stats']['equity'],
        metrics=context['stats']['metrics']
    )

    return flask.Response(
        response=dumps(overview),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/metrics/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_metrics(context_id):
    """
    Get metrics data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context.

    Returns:
        Response: JSON response containing formatted metrics data.
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = Formatter._format_metrics(context['stats']['metrics'])
    
    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/trades/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_trades(context_id):
    """
    Get trades data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context.

    Returns:
        Response: JSON response containing formatted trades data.
    """

    context = flask.current_app.strategy_contexts[context_id]
    trades = Formatter._format_trades(
        completed_deals_log=context['instance'].completed_deals_log,
        open_deals_log=context['instance'].open_deals_log
    )

    return flask.Response(
        response=dumps(trades),
        status=200,
        mimetype='application/json'
    )