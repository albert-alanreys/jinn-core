from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, current_app

from ..errors.contexts import handle_context_api_errors
from ..formatting.report import (
    format_overview_metrics,
    format_performance_metrics,
    format_trade_metrics,
    format_risk_metrics,
    format_trades
)


report_bp = Blueprint('report_api', __name__, url_prefix='/api/report')


@report_bp.route('/metrics/<string:context_id>/overview', methods=['GET'])
@handle_context_api_errors
def get_overview_metrics(context_id: str) -> Response:
    """
    Get formatted overview metrics data for a specific strategy context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = current_app.strategy_contexts[context_id]
    metrics = format_overview_metrics(
        metrics=context['metrics']['overview'],
        completed_deals_log=context['instance'].completed_deals_log
    )

    return Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/metrics/<string:context_id>/performance', methods=['GET'])
@handle_context_api_errors
def get_performance_metrics(context_id: str) -> Response:
    """
    Get formatted performance metrics for a specific strategy context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = current_app.strategy_contexts[context_id]
    metrics = format_performance_metrics(
        context['metrics']['performance']
    )
    
    return Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/metrics/<string:context_id>/trades', methods=['GET'])
@handle_context_api_errors
def get_trade_metrics(context_id: str) -> Response:
    """
    Get formatted trade-related metrics for a specific strategy context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = current_app.strategy_contexts[context_id]
    metrics = format_trade_metrics(
        context['metrics']['trades']
    )
    
    return Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/metrics/<string:context_id>/risk', methods=['GET'])
@handle_context_api_errors
def get_risk_metrics(context_id: str) -> Response:
    """
    Get formatted risk-related metrics for a specific strategy context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted metrics
    """

    context = current_app.strategy_contexts[context_id]
    metrics = format_risk_metrics(context['metrics']['risk'])
    
    return Response(
        response=dumps(metrics),
        status=200,
        mimetype='application/json'
    )


@report_bp.route('/trades/<string:context_id>', methods=['GET'])
@handle_context_api_errors
def get_trades(context_id: str) -> Response:
    """
    Get trades data for a specific strategy context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted trades
    """

    context = current_app.strategy_contexts[context_id]
    trades = format_trades(
        completed_deals_log=context['instance'].completed_deals_log,
        open_deals_log=context['instance'].open_deals_log
    )

    return Response(
        response=dumps(trades),
        status=200,
        mimetype='application/json'
    )