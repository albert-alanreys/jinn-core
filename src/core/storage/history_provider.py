from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

import numpy as np

from .db_manager import DBManager

if TYPE_CHECKING:
    from src.core.enums import Market
    from src.services.automation.api_clients.binance import BinanceREST
    from src.services.automation.api_clients.bybit import BybitREST


class HistoryProvider():
    def __init__(self) -> None:
        self.db_manager = DBManager()
        self.logger = getLogger(__name__)

    def fetch_data(
        self,
        client: 'BinanceREST | BybitREST',
        market: 'Market',
        symbol: str,
        interval: str,
        start: str,
        end: str 
    ) -> dict:
        p_precision = client.get_price_precision(symbol)
        q_precision = client.get_qty_precision(symbol)

        klines = self._fetch_klines(
            client=client,
            market=market,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        return {
            'market': market,
            'symbol': symbol,
            'interval': interval,
            'p_precision': p_precision,
            'q_precision': q_precision,
            'klines': klines,
            'start': start,
            'end': end
        }

    def _fetch_klines(
        self,
        client: 'BinanceREST | BybitREST',
        market: 'Market',
        symbol: str,
        interval: str,
        start: str,
        end: str
    ) -> np.ndarray:
        request_required = False

        database_name = f'{client.EXCHANGE.lower()}.db'
        table_name = f'{market.value}_{symbol}_{interval}'

        start_ms = int(
            datetime.strptime(start, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        end_ms = int(
            datetime.strptime(end, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        start_to_request_ms = start_ms
        end_to_request_ms = end_ms

        klines = self.db_manager.load_many(database_name, table_name)

        if not klines or len(klines) < 2:
            request_required = True

        if not request_required and start_ms < klines[0][0]:
            availability = self.db_manager.load_one(
                database_name=database_name,
                table_name='klines_metadata',
                key_column='klines_key',
                key_value=table_name
            )

            if not availability:
                end_to_request_ms = max(end_ms, klines[-1][0])
                request_required = True

        if not request_required and end_ms > klines[-1][0]:
            kline_ms = klines[1][0] - klines[0][0]
            now_ms = int(datetime.now().timestamp() * 1000)
            end_to_request_ms = min(end_ms, now_ms - kline_ms)

            if bool((end_to_request_ms - klines[-1][0]) // kline_ms):
                start_to_request_ms = min(start_ms, klines[0][0])
                request_required = True

        if request_required:
            klines = self._fetch_klines_from_exchange(
                client=client,
                market=market,
                symbol=symbol,
                interval=interval,
                start=start_to_request_ms,
                end=end_to_request_ms
            )

            if self._has_realtime_kline(klines):
                klines = klines[:-1]

            columns = {
                'time': 'TIMESTAMP PRIMARY KEY',
                'open': 'REAL',
                'high': 'REAL',
                'low': 'REAL',
                'close': 'REAL',
                'volume': 'REAL',
            }
            self.db_manager.save(
                database_name=database_name,
                table_name=table_name,
                columns=columns,
                data=klines,
                drop=True
            )

            if self._has_first_historical_kline(klines, start_ms):
                columns = {
                    'klines_key': 'TEXT PRIMARY KEY',
                    'has_first_bar': 'BOOLEAN'
                }
                table_data = [[table_name, True]]

                self.db_manager.save(
                    database_name=database_name,
                    table_name='klines_metadata',
                    columns=columns,
                    data=table_data,
                    drop=False
                )

        klines = np.array(klines, dtype=np.float64)
        klines = klines[
            (klines[:, 0] >= start_ms) &
            (klines[:, 0] <= end_ms)
        ]

        if klines.size == 0:
            start_str = (
                datetime.fromtimestamp(start_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No klines available | '
                f'{client.EXCHANGE} | '
                f'{market.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{start_str} → {end_str}'
            )
        
        return klines

    def _fetch_klines_from_exchange(
        self,
        client: 'BinanceREST | BybitREST',
        market: 'Market',
        symbol: str,
        interval: str,
        start: int,
        end: int
    ) -> list:
        self.logger.info(
            f'Requesting klines | '
            f'{client.EXCHANGE} | '
            f'{market.value} | '
            f'{symbol} | '
            f'{interval}'
        )

        klines = client.get_historical_klines(
            market=market,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        if not klines:
            start_str = (
                datetime.fromtimestamp(start / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No klines available | Period: {start_str} → {end_str}'
            )

        return [
            [float(value) for value in kline[:6]]
            for kline in klines
        ]
    
    def _has_first_historical_kline(self, klines: list, start: int) -> bool:
        kline_ms = klines[1][0] - klines[0][0]
        return bool((klines[0][0] - start) // kline_ms)
    
    def _has_realtime_kline(self, klines: list) -> bool:
        now_ms = int(datetime.now().timestamp() * 1000)
        kline_ms = klines[1][0] - klines[0][0]
        return not bool((now_ms - klines[-1][0]) // kline_ms)