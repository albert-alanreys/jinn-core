from __future__ import annotations
from json import dumps

from flask import Blueprint, Response, request

from src.features.execution import execution_service
from ..errors.contexts import with_context_error_handling
from ..formatting.contexts import format_execution_contexts


execution_bp = Blueprint(
    name='execution_api',
    import_name=__name__,
    url_prefix='/api/contexts/execution'
)


@execution_bp.route('', methods=['GET'])
@with_context_error_handling
def get_all_contexts() -> Response:
    """
    Get summary information for all strategy execution contexts.

    Returns:
        Response: JSON response containing base context data
                  for all active strategy execution contexts
    """

    contexts = execution_service.contexts
    formatted = format_execution_contexts(contexts)
    return Response(
        response=dumps(formatted),
        status=200,
        mimetype='application/json'
    )


@execution_bp.route('/<string:context_id>', methods=['GET'])
@with_context_error_handling
def get_context(context_id: str) -> Response:
    """
    Get summary information for a specific strategy execution context.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Query Parameters:
        updated_after (float, optional): Unix timestamp in milliseconds.
            If provided, the endpoint returns an empty response
            if the context has no newer klines since this time.

    Returns:
        Response: JSON response containing base context data.
                  Returns an empty JSON object if no updates.
    """

    context = execution_service.get_context(context_id)
    klines = context['market_data']['klines']
    updated_after = request.args.get('updated_after', type=int)

    if updated_after and klines:
        last_kline_time = int(klines[-1, 0])
        if last_kline_time <= updated_after:
            return Response(
                response=dumps({}),
                status=200,
                mimetype='application/json'
            )

    formatted = format_execution_contexts({context_id: context})
    return Response(
        response=dumps(formatted),
        status=200,
        mimetype='application/json'
    )


@execution_bp.route('/<string:context_id>', methods=['PATCH'])
@with_context_error_handling
def update_context(context_id: str) -> Response:
    """
    Update a parameter in a strategy context and recompute metrics.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Request Body:
        {
            "param": "strategy_parameter_name",
            "value": "new_value"
        }

    Returns:
        Response: JSON response with operation status
    """

    data = request.get_json()
    param = data.get('param')
    value = data.get('value')

    execution_service.update_context(context_id, param, value)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )


@execution_bp.route('/<string:context_id>', methods=['DELETE'])
@with_context_error_handling
def delete_context(context_id: str) -> Response:
    """
    Remove strategy context from active execution contexts.

    Path Parameters:
        context_id: Unique identifier of the strategy context

    Returns:
        Response: JSON response with operation status
    """

    execution_service.delete_context(context_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )