from json import dumps

import flask

from src.api.formatting import Formatter
from src.api.utils.error_handling import handle_api_errors


report_bp = flask.Blueprint(
    name='report_api',
    import_name=__name__,
    url_prefix='/api/report'
)


@report_bp.route('/overview/<string:context_id>/metrics', methods=['GET'])
@handle_api_errors
def get_overview_metrics(context_id):
    """
    Get formatted overview metrics data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context.

    Returns:
        Response: JSON response containing formatted metrics data.
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = Formatter._format_overview_metrics(
        metrics=context['stats']['metrics'],
        completed_deals_log=context['instance'].completed_deals_log
    )

    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/overview/<string:context_id>/equity', methods=['GET'])
@handle_api_errors
def get_overview_equity(context_id):
    """
    Get formatted equity curve data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context.

    Returns:
        Response: JSON response containing formatted equity data.
    """

    context = flask.current_app.strategy_contexts[context_id]
    equity = Formatter._format_overview_equity(
        completed_deals_log=context['instance'].completed_deals_log,
        equity=context['stats']['equity']
    )

    return flask.Response(
        response=dumps(equity),
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