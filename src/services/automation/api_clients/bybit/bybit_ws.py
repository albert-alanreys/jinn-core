from typing import Any

from src.core.utils.singleton import singleton
from .ws.kline_stream import KlineStream


@singleton
class BybitWebSocket:
    def __init__(self):
        self.kline = KlineStream()

    def __getattr__(self, name: str) -> Any:
        for subclient_name in ('kline',):
            try:
                subclient = object.__getattribute__(self, subclient_name)
                return getattr(subclient, name)
            except AttributeError:
                continue

        raise AttributeError(f'BybitWebSocket has no attribute "{name}"')