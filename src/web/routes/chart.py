from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, current_app

from ..errors.contexts import handle_context_api_errors
from ..formatting.chart import (
    format_klines,
    format_indicators,
    format_deals
)


chart_bp = Blueprint('chart_api', __name__, url_prefix='/api/chart')


@chart_bp.route('/klines/<string:context_id>', methods=['GET'])
@handle_context_api_errors
def get_klines(context_id: str) -> Response:
    """
    Get formatted klines (candlestick) data for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted klines data
    """

    context = current_app.strategy_contexts[context_id]
    klines = format_klines(
        context['market_data']['klines']
    )

    return Response(
        response=dumps(klines),
        status=200,
        mimetype='application/json'
    )


@chart_bp.route('/indicators/<string:context_id>', methods=['GET'])
@handle_context_api_errors
def get_indicators(context_id: str) -> Response:
    """
    Get calculated technical indicators for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted indicators data
    """

    context = current_app.strategy_contexts[context_id]
    indicators = format_indicators(
        context['market_data'],
        context['instance'].indicators
    )

    return Response(
        response=dumps(indicators),
        status=200,
        mimetype='application/json'
    )


@chart_bp.route('/deals/<string:context_id>', methods=['GET'])
@handle_context_api_errors
def get_deals(context_id: str) -> Response:
    """
    Get deals (entry/exit points) for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted deals data
    """

    context = current_app.strategy_contexts[context_id]
    deals = format_deals(
        context['instance'].completed_deals_log,
        context['instance'].open_deals_log
    )

    return Response(
        response=dumps(deals),
        status=200,
        mimetype='application/json'
    )