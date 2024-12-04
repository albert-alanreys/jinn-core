import logging

import numpy as np

import src.model.enums as enums
from src.model.db_manager import DBManager
from src.model.api_clients.binance_client import BinanceClient
from src.model.api_clients.bybit_client import BybitClient


class Ingester:
    def __init__(self, ingestion_info: dict) -> None:
        self.exchange = ingestion_info['exchange']
        self.market = ingestion_info['market']
        self.symbol = ingestion_info['symbol']
        self.interval = ingestion_info['interval']
        self.start = ingestion_info['start']
        self.end = ingestion_info['end']

        self.logger = logging.getLogger(__name__)
        self.db_manager = DBManager()

    def ingeste(self) -> None:
        self.logger.info(f'Data ingestion for {self.symbol}')

        match self.exchange:
            case enums.Exchange.BINANCE:
                client = BinanceClient()
            case enums.Exchange.BYBIT:
                client = BybitClient()

        raw_klines = client.fetch_historical_klines(
            symbol=self.symbol,
            market=self.market,
            interval=self.interval,
            start=self.start,
            end=self.end
        )
        klines = np.array(raw_klines)[:, :6].astype(float)

        match self.market:
            case enums.Market.SPOT:
                postfix = '_SPOT'
            case enums.Market.FUTURES:
                postfix = '_FUTURES'

        self.db_manager.load_data(
            db_name=f'{self.exchange.value.capitalize()}.db',
            table=f'{self.symbol}{postfix}_{self.interval.value}',
            columns={
                'time': 'TIMESTAMP',
                'open': 'REAL',
                'high': 'REAL',
                'low': 'REAL',
                'close': 'REAL',
                'volume': 'REAL',
            },
            data=klines
        )