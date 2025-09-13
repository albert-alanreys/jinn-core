from __future__ import annotations
from typing import TYPE_CHECKING

from src.core.strategies import strategy_registry

if TYPE_CHECKING:
    from src.features.execution.models import (
        StrategyContext as ExecutionContext,
        ContextStatus as ExecutionContextStatus
    )
    from src.features.optimization.models import (
        StrategyContext as OptimizationContext,
        ContextStatus as OptimizationContextStatus
    )
    from .models import (
        ExecutionContextResponse,
        OptimizationContextResponse
    )


def format_execution_contexts(
    contexts: ExecutionContext
) -> dict[str, ExecutionContextResponse]:
    """
    Format strategy execution contexts.

    Args:
        contexts: Dictionary of strategy contexts

    Returns:
        dict: Formatted context data
    """

    result = {}
    for context_id, context in contexts.items():
        market_data = context['market_data']
        min_move = market_data['p_precision']
        precision = (
            len(str(min_move).split('.')[1])
            if '.' in str(min_move) else 0
        )

        result[context_id] = {
            'strategy': context['name'],
            'symbol': market_data['symbol'],
            'interval': market_data['interval'].value,
            'exchange': context['exchange'],
            'isLive': context['is_live'],
            'minMove': min_move,
            'precision': precision,
            'params': context['strategy'].params,
        }

    return result


def format_optimization_contexts(
        contexts: OptimizationContext
    ) -> dict[str, OptimizationContextResponse]:
    """
    Format strategy optimization contexts.

    Args:
        contexts: Dictionary of strategy contexts

    Returns:
        dict: Formatted context data
    """

    result = {}
    for context_id, context in contexts.items():
        market_data = context['market_data']

        result[context_id] = {
            'strategy': context['name'],
            'symbol': market_data['symbol'],
            'interval': market_data['interval'].value,
            'exchange': context['exchange'],
            'start': market_data['start'],
            'end': market_data['end'],
            'params': {
                **strategy_registry[context['name']].get_params(),
                **context['optimized_params'],
            },
        }

    return result


def format_contexts_statuses(
    statuses: dict[str, ExecutionContextStatus | OptimizationContextStatus]
) -> dict[str, str]:
    """
    Format strategy execution context statuses for frontend.
    Converts ContextStatus enums to string values.

    Args:
        statuses: Dictionary of strategy context statuses

    Returns:
        dict[str, str]: Status data with enum values as strings
    """
    
    return {
        context_id: status.value
        for context_id, status in statuses.items()
    }