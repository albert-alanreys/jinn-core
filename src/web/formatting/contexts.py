def format_contexts(strategy_contexts: dict) -> dict:
    """
    Formats raw strategy contexts into a concise dictionary suitable.

    Args:
        strategy_contexts: Dictionary of strategy contexts

    Returns:
        dict: Formatted context data
    """

    result = {}

    for cid, context in strategy_contexts.items():
        market_data = context['market_data']
        instance = context['instance']
        min_move = market_data['p_precision']
        precision = (
            len(str(min_move).split('.')[1])
            if '.' in str(min_move) else 0
        )

        result[cid] = {
            'name': '-'.join(
                word.capitalize()
                for word in context['name'].split('_')
            ),
            'exchange': context['client'].exchange_name,
            'symbol': market_data['symbol'],
            'interval': market_data['interval'],
            'minMove': min_move,
            'precision': precision,
            'strategyParams': {
                k: v 
                for k, v in instance.params.items() 
                if k != 'feeds'
            },
            'indicatorOptions': instance.indicator_options
        }

    return result