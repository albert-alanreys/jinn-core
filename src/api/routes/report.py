from json import dumps

import flask

import src.api.formatting.report as report_formatter
from src.api.utils import handle_api_errors


report_bp = flask.Blueprint(
    name='report_api',
    import_name=__name__,
    url_prefix='/api/report'
)


@report_bp.route('/metrics/<string:context_id>/overview', methods=['GET'])
@handle_api_errors
def get_overview_metrics(context_id: str) -> flask.Response:
    """
    Get formatted overview metrics data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = report_formatter.format_overview_metrics(
        metrics=context['metrics']['overview'],
        completed_deals_log=context['instance'].completed_deals_log
    )

    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/metrics/<string:context_id>/performance', methods=['GET'])
@handle_api_errors
def get_performance_metrics(context_id: str) -> flask.Response:
    """
    Get formatted performance metrics for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = report_formatter.format_performance_metrics(
        context['metrics']['performance']
    )
    
    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )

@report_bp.route('/metrics/<string:context_id>/trades', methods=['GET'])
@handle_api_errors
def get_trade_metrics(context_id: str) -> flask.Response:
    """
    Get formatted trade-related metrics for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = report_formatter.format_trade_metrics(
        context['metrics']['trades']
    )
    
    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )

@report_bp.route('/metrics/<string:context_id>/risk', methods=['GET'])
@handle_api_errors
def get_risk_metrics(context_id: str) -> flask.Response:
    """
    Get formatted risk-related metrics for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = flask.current_app.strategy_contexts[context_id]
    metrics = report_formatter.format_risk_metrics(context['metrics']['risk'])
    
    return flask.Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )

@report_bp.route('/trades/<string:context_id>', methods=['GET'])
@handle_api_errors
def get_trades(context_id: str) -> flask.Response:
    """
    Get trades data for a specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted trades
    """

    context = flask.current_app.strategy_contexts[context_id]
    trades = report_formatter.format_trades(
        completed_deals_log=context['instance'].completed_deals_log,
        open_deals_log=context['instance'].open_deals_log
    )

    return flask.Response(
        response=dumps(trades),
        status=200,
        mimetype='application/json'
    )