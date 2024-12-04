import datetime

import numpy as np

from src.db_manager import DBManager
from src.enums import *


class DBReader:
    def __init__(self) -> None:
        self.db_manager = DBManager()

    def read(
        self,
        symbol_asset: SymbolAsset,
        start_time: str,
        end_time: str
    ) -> dict:
        exchange_data = {}
        start_time = int(
            datetime.datetime.strptime(
                start_time, '%Y-%m-%d'
            ).replace(tzinfo=datetime.timezone.utc).timestamp()
        ) * 1000
        end_time = int(
            datetime.datetime.strptime(
                end_time, '%Y-%m-%d'
            ).replace(tzinfo=datetime.timezone.utc).timestamp()
        ) * 1000

        rows, column_names = self.db_manager.fetch_data(
            db_name=DBName.ON_CHAIN_DATA_DB.value,
            table=symbol_asset.asset.value,
            start_time=start_time,
            end_time=end_time
        )
        on_chain_data = {
            col: np.array([row[idx] for row in rows], dtype=np.float64)
            for idx, col in enumerate(column_names)
        }

        if symbol_asset.symbol.value != 'BTCUSDT':
            rows, column_names = self.db_manager.fetch_data(
                db_name=DBName.EXCHANGE_DATA.value,
                table='BTCUSDT',
                start_time=start_time,
                end_time=end_time
            )
            exchange_data['BTCUSDT'] = {
                col: np.array([row[idx] for row in rows], dtype=np.float64)
                for idx, col in enumerate(column_names)
            }

        if symbol_asset.symbol.value != 'ETHUSDT':
            rows, column_names = self.db_manager.fetch_data(
                db_name=DBName.EXCHANGE_DATA.value,
                table='ETHUSDT',
                start_time=start_time,
                end_time=end_time
            )
            exchange_data['ETHUSDT'] = {
                col: np.array([row[idx] for row in rows], dtype=np.float64)
                for idx, col in enumerate(column_names)
            }

        rows, column_names = self.db_manager.fetch_data(
            db_name=DBName.EXCHANGE_DATA.value,
            table=symbol_asset.symbol.value,
            start_time=start_time,
            end_time=end_time
        )
        exchange_data[symbol_asset.symbol.value] = {
            col: np.array([row[idx] for row in rows], dtype=np.float64)
            for idx, col in enumerate(column_names)
        }

        return {
            'on_chain_data': on_chain_data,
            'exchange_data': exchange_data,
        }