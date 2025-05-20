import os
import sqlite3
from logging import getLogger


class DBManager():
    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def load_many(self, database_name: str, table_name: str) -> list:
        try:
            self._connect(database_name)

            self.cursor.execute(
                'SELECT name FROM sqlite_master '
                'WHERE type="table" AND name=?',
                (table_name,)
            )

            if not self.cursor.fetchone():
                return []

            self.cursor.execute(f'SELECT * FROM "{table_name}"')
            return self.cursor.fetchall()
        except Exception as e:
            self.logger.error(
                f'Failed to load data from {table_name}: '
                f'{type(e).__name__} - {e}'
            )
            return []
        finally:
            self._disconnect()

    def _connect(self, database_name: str) -> None:
        db_path = os.path.join(
            os.path.dirname(__file__), 'databases', database_name
        )
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
    
    def _disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()

        if self.connection:
            self.connection.close()

    def load_one(
        self,
        database_name: str,
        table_name: str,
        key_column: str,
        key_value: str
    ) -> list:
        try:
            self._connect(database_name)

            self.cursor.execute(
                'SELECT name FROM sqlite_master '
                'WHERE type="table" AND name=?',
                (table_name,)
            )

            if not self.cursor.fetchone():
                return []

            self.cursor.execute(
                f'SELECT * FROM "{table_name}" WHERE {key_column} = ?',
                (key_value,)
            )
            row = self.cursor.fetchone()

            if row is None:
                return []
            
            return row
        except Exception as e:
            self.logger.error(
                f'Failed to load row from {table_name}: '
                f'{type(e).__name__} - {e}'
            )
            return []
        finally:
            self._disconnect()

    def save(
        self,
        database_name: str,
        table_name: str,
        columns: dict,
        data: list,
        drop: bool
    ) -> None:
        try:
            self._connect(database_name)

            if drop:
                self.cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

            self.cursor.execute(
                'SELECT name FROM sqlite_master '
                'WHERE type="table" AND name=?',
                (table_name,)
            )
            
            if not self.cursor.fetchone():
                column_defs = [
                    f'"{col}" {dtype}' for col, dtype in columns.items()
                ]
                self.cursor.execute(
                    f'CREATE TABLE IF NOT EXISTS "{table_name}" '
                    f'({", ".join(column_defs)})'
                )

            query_to_insert = (
                f'INSERT {"" if drop else "OR IGNORE"} INTO "{table_name}" '
                f'VALUES ({", ".join(['?'] * len(columns))})'
            )

            for row in data:
                self.cursor.execute(query_to_insert, row)

            self.connection.commit()
        except Exception as e:
            self.logger.error(
                f'Failed to save data into {table_name}: '
                f'{type(e).__name__} - {e}'
            )
        finally:
            self._disconnect()