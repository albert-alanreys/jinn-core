from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.features.execution.models import (
        StrategyContext as ExecutionContext
    )


def format_execution_contexts(contexts: ExecutionContext) -> dict[str, Any]:
    """
    Format strategy contexts for frontend display.

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
            'name': context['name'],
            'exchange': context['exchange'],
            'isLive': context['is_live'],
            'symbol': market_data['symbol'],
            'interval': market_data['interval'],
            'minMove': min_move,
            'precision': precision,
            'strategyParams': {
                k: v 
                for k, v in strategy.params.items() 
                if k != 'feeds'
            },
            'indicatorOptions': strategy.indicator_options
        }

    return result