from __future__ import annotations
from json import dumps

from flask import Blueprint, Response

from src.core.strategies import strategy_registry
from src.infrastructure.exchanges.models import Exchange, Interval


context_bp = Blueprint('context_api', __name__, url_prefix='/api/context')


@context_bp.route('/exchanges', methods=['GET'])
def get_exchanges() -> Response:
    """
    Get supported cryptocurrency exchanges.

    Returns:
        Response: JSON response containing supported exchanges
    """
    
    return Response(
        response=dumps([exchange.value for exchange in Exchange]),
        status=200,
        mimetype='application/json'
    )


@context_bp.route('/intervals', methods=['GET'])
def get_intervals() -> Response:
    """
    Get supported kline intervals.

    Returns:
        Response: JSON response containing supported intervals
    """
    
    return Response(
        response=dumps([interval.value for interval in Interval]),
        status=200,
        mimetype='application/json'
    )


@context_bp.route('/strategies', methods=['GET'])
def get_strategies() -> Response:
    """
    Get registry of all available strategies with their parameters.

    Returns:
        Response: JSON response containing strategy registry
    """
    
    strategy_data = {}
    
    for strategy_name, strategy_class in strategy_registry.items():
        params = {
            param_name: param_value
            for param_name, param_value in strategy_class.params.items()
        }
        strategy_data[strategy_name] = {
            'name': strategy_name,
            'params': params,
        }
    
    return Response(
        response=dumps(strategy_data),
        status=200,
        mimetype='application/json'
    )