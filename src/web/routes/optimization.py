from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, request

from src.features.optimization import optimization_service
from ..errors.contexts import with_context_error_handling
from ..formatting.contexts import format_optimization_contexts


optimization_bp = Blueprint(
    name='optimization_api',
    import_name=__name__,
    url_prefix='/api/contexts/optimization'
)


@optimization_bp.route('', methods=['POST'])
@with_context_error_handling
def add_contexts() -> Response:
    """
    Add new strategy optimization contexts to the processing queue.

    Request Body:
        {
            "context_id_1": {
                "strategy": "strategy_name",
                "symbol": "BTCUSDT",
                "interval": "1h",
                "exchange": "BINANCE",
                "start": "2020-01-01",
                "end": "2024-12-31"
            },
            "context_id_2": {...}
        }

    Returns:
        Response: JSON response containing list of successfully
                  queued context identifiers
    """

    configs = request.get_json()
    added = optimization_service.add_contexts(configs)
    return Response(
        response=dumps({'added': added}),
        status=201,
        mimetype='application/json'
    )


@optimization_bp.route('', methods=['GET'])
@with_context_error_handling
def get_all_contexts() -> Response:
    """
    Get summary information for all strategy optimization contexts.

    Returns:
        Response: JSON response containing base context data
                  for all active strategy optimization contexts
    """

    contexts = optimization_service.contexts
    formatted = format_optimization_contexts(contexts)
    return Response(
        response=dumps(formatted),
        status=200,
        mimetype='application/json'
    )


@optimization_bp.route('/<string:context_id>', methods=['GET'])
@with_context_error_handling
def get_context(context_id: str) -> Response:
    """
    Get summary information for a specific strategy optimization context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing base context data
    """

    context = optimization_service.get_context(context_id)
    formatted = format_optimization_contexts({context_id: context})
    return Response(
        response=dumps(formatted),
        status=200,
        mimetype='application/json'
    )


@optimization_bp.route('/<string:context_id>', methods=['DELETE'])
@with_context_error_handling
def delete_context(context_id: str) -> Response:
    """
    Remove strategy context from active optimization contexts.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response with operation status
    """

    optimization_service.delete_context(context_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )


@optimization_bp.route('/status', methods=['GET'])
@with_context_error_handling
def get_all_contexts_status() -> Response:
    """
    Get current status information for all strategy optimization contexts.

    Returns:
        Response: JSON response containing status data
                  for all strategy optimization contexts
    """

    statuses = optimization_service.get_contexts_status()
    return Response(
        response=dumps(statuses),
        status=200,
        mimetype='application/json'
    )


@optimization_bp.route('/<string:context_id>/status', methods=['GET'])
@with_context_error_handling
def get_context_status(context_id: str) -> Response:
    """
    Get current status information for a specific
    strategy optimization context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response containing context status.
                  Returns null if context doesn't exist.
    """

    status = optimization_service.get_context_status(context_id)
    return Response(
        response=dumps({'status': status}),
        status=200,
        mimetype='application/json'
    )