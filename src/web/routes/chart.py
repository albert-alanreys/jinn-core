from __future__ import annotations
from json import dumps

from flask import Blueprint, Response

from src.features.execution import execution_service
from ..errors.contexts import with_context_error_handling
from ..formatting.chart import (
    format_klines,
    format_indicators,
    format_deals
)


chart_bp = Blueprint('chart_api', __name__, url_prefix='/api/chart')


@chart_bp.route('/klines/<string:context_id>', methods=['GET'])
@with_context_error_handling
def get_klines(context_id: str) -> Response:
    """
    Get formatted klines data for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted klines data
    """

    context = execution_service.get_context(context_id)
    formatted_klines = format_klines(context['market_data']['klines'])
    return Response(
        response=dumps(formatted_klines),
        status=200,
        mimetype='application/json'
    )


@chart_bp.route('/indicators/<string:context_id>', methods=['GET'])
@with_context_error_handling
def get_indicators(context_id: str) -> Response:
    """
    Get calculated technical indicators for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted indicators data
    """

    context = execution_service.get_context(context_id)
    formatted_indicators = format_indicators(
        market_data=context['market_data'],
        indicators=context['strategy'].indicators
    )
    return Response(
        response=dumps(formatted_indicators),
        status=200,
        mimetype='application/json'
    )


@chart_bp.route('/deals/<string:context_id>', methods=['GET'])
@with_context_error_handling
def get_deals(context_id: str) -> Response:
    """
    Get deals (entry/exit points) for chart visualization.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing formatted deals data
    """

    context = execution_service.get_context(context_id)
    formatted_deals = format_deals(context['strategy'])
    return Response(
        response=dumps(formatted_deals),
        status=200,
        mimetype='application/json'
    )