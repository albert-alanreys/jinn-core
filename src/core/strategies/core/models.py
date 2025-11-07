from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, TypedDict

if TYPE_CHECKING:
    import numpy as np


# --- Parameter Types ---

StrategyParam = bool | int | float
"""Type for individual strategy parameter values."""

ParamDict = dict[str, StrategyParam]
"""Dictionary of strategy parameters."""

OptParamDict = dict[str, list[StrategyParam]]
"""Dictionary of parameter ranges for optimization."""

ParamLabelDict = dict[str, str]
"""Dictionary mapping parameter names to human-readable labels."""


# --- Indicator Visualization Types ---

class IndicatorOptions(TypedDict, total=False):
    """
    Display configuration for a single indicator.
    
    All fields are optional to allow flexible configuration.
    """
    
    pane: int
    """Panel number (0 = main chart, 1+ = sub-panels)"""
    
    type: Literal['line', 'histogram']
    """Chart type for the indicator"""
    
    lineWidth: int
    """Line thickness (pixels)"""
    
    color: str
    """Encoded color value"""
    
    lineStyle: Literal[0, 1, 2, 3, 4]
    """
    Line pattern:
    - 0: solid
    - 1: dotted
    - 2: dashed
    - 3: large dashed
    - 4: sparse dotted
    """
    
    lineType: Literal[0, 1, 2]
    """
    Line shape:
    - 0: Simple
    - 1: WithSteps
    - 2: Curved
    """
    
    lineVisible: bool
    """Flag to control line visibility"""


IndicatorOptionsDict = dict[str, IndicatorOptions]
"""Dictionary mapping indicator names to their display options."""


class IndicatorData(TypedDict):
    """
    Complete indicator data including configuration and values.
    """
    
    options: IndicatorOptions
    """Reference to display configuration"""
    
    values: np.ndarray
    """Sequence of indicator values"""
    
    colors: np.ndarray | None
    """Optional sequence of point-specific colors"""


IndicatorDict = dict[str, IndicatorData]
"""Dictionary of all indicators to render."""


# --- Feed Configuration Types ---

FeedsConfig = dict[str, dict[str, list[Any]]]
"""
Dictionary of market data feed configurations.

Structure:
{
    'klines': {
        'feed_name': ['symbol', Interval],
        ...
    }
}
"""