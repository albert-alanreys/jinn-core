from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.features.execution.models import (
        StrategyContext as ExecutionContext
    )
    from src.features.optimization.models import (
        StrategyContext as OptimizationContext
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
        strategy = context['strategy']
        market_data = context['market_data']
        min_move = market_data['p_precision']
        precision = (
            len(str(min_move).split('.')[1])
            if '.' in str(min_move) else 0
        )

        result[context_id] = {
            'strategy': context['name'],
            'symbol': market_data['symbol'],
            'interval': market_data['interval'],
            'exchange': context['exchange'],
            'isLive': context['is_live'],
            'minMove': min_move,
            'precision': precision,
            'params': strategy.all_params,
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
            'interval': market_data['interval'],
            'exchange': context['exchange'],
            'start': market_data['start'],
            'end': market_data['end'],
            'params': context['optimized_params'],
        }

    return result