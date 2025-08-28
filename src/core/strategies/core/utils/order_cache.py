from __future__ import annotations
from logging import getLogger

from src.infrastructure.db import db_manager


logger = getLogger(__name__)


def load_order_cache(
    strategy: str,
    exchange: str,
    symbol: str
) -> dict[str, list[str]]:
    """
    Load cached order IDs for a given strategy, exchange,
    and symbol from SQLite database.

    Args:
        strategy: Strategy name
        exchange: Exchange name  
        symbol: Trading symbol

    Returns:
        dict[str, list[str]]: Dictionary containing:
            - 'stop_ids': list of stop order IDs
            - 'limit_ids': list of limit order IDs
    """
    
    db_name = f'{exchange.lower()}.db'
    table_name = 'order_identifiers'
    key = f'{strategy}_{symbol}'.lower()
    
    try:
        row = db_manager.fetch_one(
            database_name=db_name,
            table_name=table_name,
            key_column='key',
            key_value=key
        )
        
        if not row:
            return {'stop_ids': [], 'limit_ids': []}
        
        stop_ids = _parse_ids_string(row[1]) if row[1] else []
        limit_ids = _parse_ids_string(row[2]) if row[2] else []
        
        return {
            'stop_ids': stop_ids,
            'limit_ids': limit_ids
        }
    except Exception as e:
        logger.error(
            f'Failed to load order cache for {key}: '
            f'{type(e).__name__} - {e}'
        )
        return {'stop_ids': [], 'limit_ids': []}


def save_order_cache(
    strategy: str,
    exchange: str,
    symbol: str,
    order_ids: dict[str, list[str]]
) -> None:
    """
    Save order IDs to SQLite database for a given strategy,
    exchange, and symbol.

    Args:
        strategy: Strategy name
        exchange: Exchange name
        symbol: Trading symbol
        order_ids: Dictionary containing:
            - 'stop_ids': list of stop order IDs
            - 'limit_ids': list of limit order IDs
    """
    
    db_name = f'{exchange.lower()}.db'
    table_name = 'order_identifiers'
    key = f'{strategy}_{symbol}'.lower()
    
    stop_ids_str = _format_ids_list(order_ids.get('stop_ids', []))
    limit_ids_str = _format_ids_list(order_ids.get('limit_ids', []))
    
    columns = {
        'key': 'TEXT PRIMARY KEY',
        'stop_ids': 'TEXT',
        'limit_ids': 'TEXT'
    }
    row = (key, stop_ids_str, limit_ids_str)
    
    try:
        db_manager.insert_one(
            database_name=db_name,
            table_name=table_name,
            columns=columns,
            row=row,
            replace=True
        )
    except Exception as e:
        logger.error(
            f'Failed to save order cache for {key}: '
            f'{type(e).__name__} - {e}'
        )


def _parse_ids_string(ids_str: str) -> list[str]:
    """
    Parse comma-separated string of IDs into a list.
    
    Args:
        ids_str: Comma-separated string of IDs
        
    Returns:
        list[str]: List of order IDs
    """

    if not ids_str or ids_str.strip() == '':
        return []
    
    return [id_str.strip() for id_str in ids_str.split(',') if id_str.strip()]


def _format_ids_list(ids_list: list[str]) -> str:
    """
    Format list of IDs into comma-separated string.
    
    Args:
        ids_list: List of order IDs
        
    Returns:
        str: Comma-separated string of IDs
    """

    if not ids_list:
        return ''
    
    return ','.join(str(id_val) for id_val in ids_list)