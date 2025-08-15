from ast import literal_eval
from json import dumps

from flask import Blueprint, Response, current_app, request

from src.api.errors.contexts import handle_context_api_errors
from src.api.formatting.contexts import format_contexts
from src.features.backtesting import BacktestingService


contexts_bp = Blueprint('contexts_api', __name__, url_prefix='/api/contexts')


@contexts_bp.route('', methods=['GET'])
@handle_context_api_errors
def get_all_contexts() -> Response:
    """
    Get summary information for all strategy contexts.

    Returns:
        Response: JSON response containing summarized data 
                  for all active strategy contexts
    """

    contexts = format_contexts(current_app.strategy_contexts)
    return Response(
        response=dumps(contexts),
        status=200,
        mimetype='application/json'
    )


@contexts_bp.route('/<string:context_id>', methods=['GET'])
@handle_context_api_errors
def get_context(context_id: str) -> Response:
    """
    Get summary information for specific strategy context.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response containing base context data
    """

    context = format_contexts(
        {context_id: current_app.strategy_contexts[context_id]}  
    )
    return Response(
        response=dumps(context),
        status=200,
        mimetype='application/json'
    )


@contexts_bp.route('/<string:context_id>', methods=['PATCH'])
@handle_context_api_errors
def update_context(context_id: str) -> Response:
    """
    Update parameter in strategy context and restart strategy.

    Args:
        context_id (str): Unique identifier of the strategy context

    Request Body:
        {
            "param": "strategy_parameter_name",
            "value": "new_value"
        }

    Returns:
        Response: JSON response with operation status
    """

    def _parse_value(raw):
        if isinstance(raw, list):
            return [float(x) for x in raw]

        if isinstance(raw, str):
            try:
                return literal_eval(raw.capitalize())
            except (ValueError, SyntaxError):
                return raw.capitalize()

        return raw

    data = request.get_json()
    param = data.get('param')
    raw_value = data.get('value')

    context = current_app.strategy_contexts[context_id]
    instance = context['instance']
    params = instance.params

    old_value = params[param]
    new_value = _parse_value(raw_value)

    if (
        isinstance(old_value, (int, float)) and
        isinstance(new_value, (int, float))
    ):
        new_value = type(old_value)(new_value)
    elif type(old_value) != type(new_value):
        raise TypeError()

    params[param] = new_value
    instance = context['type'](context['client'], params)
    instance.calculate(context['market_data'])

    context['instance'] = instance
    context['metrics'] = BacktestingService.test(instance)

    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )


@contexts_bp.route('/<string:context_id>', methods=['DELETE'])
@handle_context_api_errors
def delete_context(context_id: str) -> Response:
    """
    Remove strategy context from active contexts.

    Args:
        context_id (str): Unique identifier of the strategy context

    Returns:
        Response: JSON response with operation status
    """

    current_app.strategy_contexts.pop(context_id)
    return Response(
        response=dumps({'status': 'success'}),
        status=200,
        mimetype='application/json'
    )


@contexts_bp.route('/updates', methods=['GET'])
@handle_context_api_errors
def get_updated_contexts() -> Response:
    """
    Get IDs of contexts that were recently updated and
    clear the updates buffer.

    Returns:
        Response: JSON response containing list of updated context IDs
    """

    updated_contexts = current_app.updated_contexts.copy()
    current_app.updated_contexts.clear()

    return Response(
        response=dumps(updated_contexts),
        status=200,
        mimetype='application/json'
    )