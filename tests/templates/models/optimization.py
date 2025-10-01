from typing import TypedDict


class OptimizationConfigTemplate(TypedDict):
    """Extendable optimization context config template."""

    symbol: str
    interval: str
    exchange: str
    start: str
    end: str