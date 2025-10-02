from typing import TypedDict


class BacktestingConfigTemplate(TypedDict):
    """Extendable execution context config template."""

    symbol: str
    interval: str
    exchange: str
    start: str
    end: str