import logging
from datetime import datetime, timezone

import numpy as np

import src.core.enums as enums
from src.services.automation.api_clients.binance import BinanceClient
from src.services.automation.api_clients.bybit import BybitClient
from .db_manager import DBManager


class DataManager:
    def __init__(self) -> None:
        self.db_manager = DBManager()
        self.logger = logging.getLogger(__name__)

    def get_data(
        self,
        client: BinanceClient | BybitClient,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: str,
        end: str
    ) -> np.ndarray:
        request_required = False

        if isinstance(client, BinanceClient):
            exchange = enums.Exchange.BINANCE.value.lower()
        elif isinstance(client, BybitClient):
            exchange = enums.Exchange.BYBIT.value.lower()

        database_name = f'{exchange}.db'
        table_name = f'{symbol}_{market.value}_{interval}'

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

        data = self.db_manager.load_many(database_name, table_name)

        if not data or len(data) < 2:
            request_required = True

        if not request_required and start_ms < data[0][0]:
            availability = self.db_manager.load_one(
                database_name=database_name,
                table_name='data_availability',
                key_column='data_name',
                key_value=table_name
            )

            if not availability:
                end_to_request_ms = max(end_ms, data[-1][0])
                request_required = True

        if not request_required and end_ms > data[-1][0]:
            kline_ms = data[1][0] - data[0][0]
            now_ms = int(datetime.now().timestamp() * 1000)
            end_to_request_ms = min(end_ms, now_ms - kline_ms)

            if bool((end_to_request_ms - data[-1][0]) // kline_ms):
                start_to_request_ms = min(start_ms, data[0][0])
                request_required = True

        if request_required:
            data = self._get_data_from_exchange(
                client=client,
                exchange=exchange,
                market=market,
                symbol=symbol,
                interval=interval,
                start=start_to_request_ms,
                end=end_to_request_ms
            )

            if self._has_realtime_kline(data):
                data = data[:-1]

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
                data=data,
                drop=True
            )

            if self._has_first_historical_kline(data, start_ms):
                columns = {
                    'data_name': 'TEXT PRIMARY KEY',
                    'has_first_bar': 'BOOLEAN'
                }
                table_data = [[table_name, True]]

                self.db_manager.save(
                    database_name=database_name,
                    table_name='data_availability',
                    columns=columns,
                    data=table_data,
                    drop=False
                )

        data_array = np.array(data, dtype=np.float64)
        data_array = data_array[
            (data_array[:, 0] >= start_ms) &
            (data_array[:, 0] <= end_ms)
        ]

        if data_array.size == 0:
            start_str = (
                datetime.fromtimestamp(start_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end_ms / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No data available | '
                f'{exchange.capitalize()} | '
                f'{market.value} | '
                f'{symbol} | '
                f'{interval} | '
                f'{start_str} → {end_str}'
            )
        
        return data_array

    def _get_data_from_exchange(
        self,
        client: BinanceClient | BybitClient,
        exchange: str,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: int,
        end: int
    ) -> np.ndarray:
        self.logger.info(
            f'Requesting data | '
            f'{exchange.capitalize()} | '
            f'{market.value} | '
            f'{symbol} | '
            f'{interval}'
        )

        raw_data = client.get_historical_klines(
            market=market,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end
        )

        if not raw_data:
            start_str = (
                datetime.fromtimestamp(start / 1000)
                .strftime('%Y-%m-%d')
            )
            end_str = (
                datetime.fromtimestamp(end / 1000)
                .strftime('%Y-%m-%d')
            )
            raise ValueError(
                f'No data available | Period: {start_str} → {end_str}'
            )

        return [
            [float(value) for value in row[:6]]
            for row in raw_data
        ]
    
    def _has_first_historical_kline(self, data: list, start: int) -> bool:
        kline_ms = data[1][0] - data[0][0]
        return bool((data[0][0] - start) // kline_ms)
    
    def _has_realtime_kline(self, data: list) -> bool:
        now_ms = int(datetime.now().timestamp() * 1000)
        kline_ms = data[1][0] - data[0][0]
        return not bool((now_ms - data[-1][0]) // kline_ms)