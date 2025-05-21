from typing import Any, Callable

from .ws import KlineStream


class BinanceWebSocket():
    def __init__(self, on_kline: Callable) -> None:
        self.kline = KlineStream(on_kline)

    def __getattr__(self, name: str) -> Any:
        for subclient_name in ('kline',):
            try:
                subclient = object.__getattribute__(self, subclient_name)
                return getattr(subclient, name)
            except AttributeError:
                continue

        raise AttributeError(f'BinanceWebSocket has no attribute "{name}"')