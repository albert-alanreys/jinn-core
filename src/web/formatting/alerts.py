from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.features.execution.models import AlertData


_CAMEL_CASE_MAP = {
    'alert_id': 'alertId',
    'context_id': 'contextId',
    'exchange': 'exchange',
    'type': 'type',
    'status': 'status',
    'side': 'side',
    'symbol': 'symbol',
    'qty': 'qty',
    'price': 'price',
    'time': 'time',
}


def format_alerts(alerts: list[AlertData]) -> list[dict[str, str]]:
    """
    Format alerts into JS-friendly camelCase keys.

    Args:
        alerts: List of alerts
    
    Returns:
        list: Formatted alerts
    """
    
    return [
        {
            _CAMEL_CASE_MAP[k]: v for k, v in alert.items()
            if k in _CAMEL_CASE_MAP
        }
        for alert in alerts
    ]