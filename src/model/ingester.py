import logging
import json
import os

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

        self.ingestion = []
        self.binance_client = BinanceClient()
        self.bybit_client = BybitClient()
        self.logger = logging.getLogger(__name__)
        self.db_manager = DBManager()

    def ingeste(self) -> None:
        path_to_file = os.path.abspath('ingestion.json')

        if os.path.exists(path_to_file):
            with open(path_to_file, 'r') as file:
                configs = json.load(file)
                
                for config in configs:
                    exchange = config['exchange'].upper()
                    market = config['market'].upper()
                    symbol = config['symbol'].upper()
                    interval = config['interval']
                    start = config['start']
                    end = config['end']

                    match exchange:
                        case 'BINANCE':
                            exchange = enums.Exchange.BINANCE
                            client = self.binance_client
                        case 'BYBIT':
                            exchange = enums.Exchange.BYBIT
                            client = self.bybit_client

                    match market:
                        case 'FUTURES':
                            market = enums.Market.FUTURES
                        case 'SPOT':
                            market = enums.Market.SPOT

                    interval = client.get_valid_interval(interval)
                    ingestion = {
                        'client': client,
                        'exchange': exchange,
                        'market': market,
                        'symbol': symbol,
                        'interval': interval,
                        'start': start,
                        'end': end,
                    }
                    self.ingestion.append(ingestion)
        else:
            match self.exchange:
                case enums.Exchange.BINANCE:
                    client = BinanceClient()
                case enums.Exchange.BYBIT:
                    client = BybitClient()

            self.interval = client.get_valid_interval(self.interval)
            ingestion = {
                'client': client,
                'exchange': self.exchange,
                'market': self.market,
                'symbol': self.symbol,
                'interval': self.interval,
                'start': self.start,
                'end': self.end,
            }
            self.ingestion.append(ingestion)

        ingestion_info = [
            ' • '.join(
                [
                    item['exchange'].value, item['market'].value,
                    item['symbol'], str(item['interval']),
                    item['start'], item['end']
                ]
            )
            for item in self.ingestion
        ]
        self.logger.info(
            f'Ingestion started for:\n{'\n'.join(ingestion_info)}'
        )

        for item in self.ingestion:
            try:
                raw_klines = client.get_historical_klines(
                    symbol=item['symbol'],
                    market=item['market'],
                    interval=item['interval'],
                    start=item['start'],
                    end=item['end']
                )
                klines = [
                    [float(value) for value in row[:6]]
                        for row in raw_klines
                ]
                
                if not klines:
                    continue

                match item['market']:
                    case enums.Market.SPOT:
                        postfix = '_SPOT'
                    case enums.Market.FUTURES:
                        postfix = '_FUTURES'

                self.db_manager.load_data(
                    db_name=f'{item['exchange'].value.lower()}.db',
                    table=f'{item['symbol']}{postfix}_{item['interval']}',
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
            except Exception as e:
                self.logger.error(e)