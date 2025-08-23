import os
import json
import logging


logger = logging.getLogger(__name__)


def load_order_cache(
    base_dir: str,
    strategy: str,
    exchange: str,
    symbol: str
) -> dict:
    """
    Load cached order IDs for a given strategy, exchange, and symbol.

    This function reads JSON data from the corresponding cache file and
    returns stop and limit order IDs. If the file does not exist or
    contains invalid JSON, empty lists are returned.

    Args:
        base_dir: Root cache directory
        strategy: Strategy name
        exchange: Exchange name
        symbol: Trading symbol

    Returns:
        dict: Dictionary containing:
              - 'stop_ids': list of stop order IDs
              - 'limit_ids': list of limit order IDs
    """

    path = _get_cache_path(base_dir, strategy, exchange, symbol)

    if not os.path.exists(path):
        return {'stop_ids': [], 'limit_ids': []}

    try:
        with open(path, 'r') as file:
            data = json.load(file)
        return {
            'stop_ids': data.get('stop_ids', []),
            'limit_ids': data.get('limit_ids', [])
        }
    except json.JSONDecodeError:
        logger.error(f'Failed to load JSON from {path}')
        return {'stop_ids': [], 'limit_ids': []}


def save_order_cache(
    base_dir: str,
    strategy: str,
    exchange: str,
    symbol: str,
    order_ids: dict
) -> None:
    """
    Save order IDs to cache for a given strategy, exchange, and symbol.

    The function creates the cache directory if necessary and writes
    order IDs in JSON format. Existing file will be overwritten.

    Args:
        base_dir: Root cache directory
        strategy: Strategy name
        exchange: Exchange name
        symbol: Trading symbol
        order_ids: Dictionary containing:
            - 'stop_ids': list of stop order IDs
            - 'limit_ids': list of limit order IDs
    """

    os.makedirs(base_dir, exist_ok=True)
    path = _get_cache_path(base_dir, strategy, exchange, symbol)
    data = {
        'stop_ids': order_ids.get('stop_ids', []),
        'limit_ids': order_ids.get('limit_ids', [])
    }

    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        logger.error(
            f'Failed to write JSON to {path}: {type(e).__name__} - {e}'
        )


def _get_cache_path(
    base_dir: str,
    strategy: str,
    exchange: str,
    symbol: str
) -> str:
    """
    Build the full path for the cache file.

    Args:
        base_dir: Root directory where cache files are stored
        strategy: Strategy name. Used to separate cache files per strategy
        exchange: Exchange name. Used in filename
        symbol: Trading symbol (e.g., 'BTCUSDT')

    Returns:
        str: Full path to the cache file in format:
             {base_dir}/{strategy}_{exchange}_{symbol}_ORDER_IDS.json
    """

    return os.path.join(
        base_dir, f'{strategy}_{exchange}_{symbol}_ORDER_IDS.json'
    )