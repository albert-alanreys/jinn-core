import logging
import os
import sqlite3
from datetime import datetime, timezone


class DBManager():
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.cursor = None

    def connect(self, db_name: str):
        db_path = os.path.abspath(f'src/model/databases/{db_name}')
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()

        if self.connection:
            self.connection.close()

    def load_data(
        self,
        db_name: str,
        table: str,
        columns: dict,
        data: list
    ) -> None:
        try:
            self.connect(db_name)
            self.cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
            query_columns = ', '.join(
                f"{column} {dtype} {'PRIMARY KEY' if i == 0 else ''}"
                for i, (column, dtype) in enumerate(columns.items())
            )
            self.cursor.execute(f'CREATE TABLE "{table}" ({query_columns})')
            query_to_insert = (
                f'INSERT INTO "{table}" '
                f'VALUES ({", ".join(['?'] * len(columns))})'
            )

            for row in data:
                self.cursor.execute(query_to_insert, row)

            self.connection.commit()
        except Exception as e:
            self.logger.error(f'Error while working with database: {e}')
        finally:
            self.disconnect()

    def fetch_data(
        self,
        db_name: str,
        table: str,
        start: str,
        end: str
    ) -> tuple:
        try:
            start = int(
                datetime.strptime(start, '%Y-%m-%d')
                .replace(tzinfo=timezone.utc)
                .timestamp() * 1000
            )
            end = int(
                datetime.strptime(end, '%Y-%m-%d')
                .replace(tzinfo=timezone.utc)
                .timestamp() * 1000
            )

            self.connect(db_name)
            self.cursor.execute(
                f'SELECT * FROM "{table}" WHERE time BETWEEN {start} AND {end}',
            )
            column_names = [
                description[0] for description in self.cursor.description
            ]
            rows = self.cursor.fetchall()

            if not rows:
                raise ValueError(f'No data found in table "{table}" ')

            return rows, column_names
        except Exception as e:
            self.logger.error(f'Error while working with database: {e}')
        finally:
            self.disconnect()