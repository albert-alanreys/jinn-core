from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import OptimizationConfigTemplate


optimization_config_template: OptimizationConfigTemplate = {
    'symbol': 'BTCUSDT',
    'interval': '1 Hour',
    'exchange': 'Binance',
    'start': '2018-01-01',
    'end': '2025-01-01',
}