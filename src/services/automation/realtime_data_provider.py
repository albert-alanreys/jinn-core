from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

import numpy as np

from src.core.enums import Market
from src.core.utils.singleton import singleton
from src.services.automation.api_clients.bybit import BybitWebSocket

if TYPE_CHECKING:
    from src.services.automation.api_clients.binance import BinanceClient
    from src.services.automation.api_clients.bybit import BybitREST


@singleton
class RealtimeDataProvider:
    def __init__(self) -> None:
        self.bybit_ws_client = BybitWebSocket()

        self.logger = getLogger(__name__)

    def get_data(
        self,
        client: 'BinanceClient | BybitREST',
        symbol: str,
        interval: str,
        start: str,
        end: str
    ) -> np.ndarray:
        pass
