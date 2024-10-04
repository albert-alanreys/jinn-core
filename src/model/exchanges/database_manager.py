import os
import sqlite3
from typing import Iterable


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]


class DatabaseManager(metaclass=SingletonMeta):
    def connect(self):
        self.connection = sqlite3.connect(
            os.path.abspath('src/model/exchanges/klines.db')
        )
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def select(
        self,
        exchange: str,
        symbol: str,
        interval: str | int,
        start_time: int,
        end_time: int
    ) -> tuple:
        table = f'{exchange.upper()}_{symbol}_{interval}'
        query = (
            f'''
            SELECT *
            FROM {table}
            WHERE time BETWEEN {start_time} AND {end_time}
            ORDER BY time
            '''
        )

        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            self.create(table)
            return tuple()

    def create(self, table: str) -> None:
        query = (
            f'''
            CREATE TABLE IF NOT EXISTS {table} (
            time TIMESTAMP PRIMARY KEY NOT NULL,
            open DECIMAL NOT NULL,
            high DECIMAL NOT NULL,
            low DECIMAL NOT NULL,
            close DECIMAL NOT NULL,
            volume REAL NOT NULL
            )
            '''
        )
        self.cursor.execute(query)

    def insert(
        self,
        exchange: str,
        symbol: str,
        interval: str | int,
        klines: Iterable
    ) -> None:
        table = f'{exchange.upper()}_{symbol}_{interval}'
        query = f'INSERT OR IGNORE INTO {table} VALUES (?, ?, ?, ?, ?, ?)'
        
        for kline in klines:
            self.cursor.execute(query, kline)

        self.connection.commit()