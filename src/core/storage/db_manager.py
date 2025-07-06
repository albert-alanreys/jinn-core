import os
import sqlite3
from contextlib import contextmanager
from logging import getLogger


class DBManager():
    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def fetch_all(self, database_name: str, table_name: str) -> list:
        try:
            with self._db_session(database_name) as cursor:
                query_to_check = (
                    'SELECT name FROM sqlite_master '
                    'WHERE type="table" AND name=?'
                )
                cursor.execute(query_to_check, (table_name,))

                if not cursor.fetchone():
                    return []

                cursor.execute(f'SELECT * FROM "{table_name}"')
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(
                f'Failed to load data from {table_name}: '
                f'{type(e).__name__} - {e}'
            )
            return []

    def fetch_one(
        self,
        database_name: str,
        table_name: str,
        key_column: str,
        key_value: str
    ) -> list:
        try:
            with self._db_session(database_name) as cursor:
                query_to_check = (
                    'SELECT name FROM sqlite_master '
                    'WHERE type="table" AND name=?'
                )
                cursor.execute(query_to_check, (table_name,))

                if not cursor.fetchone():
                    return []

                cursor.execute(
                    f'SELECT * FROM "{table_name}" WHERE {key_column} = ?',
                    (key_value,)
                )
                row = cursor.fetchone()

                if row is None:
                    return []
                
                return row
        except Exception as e:
            self.logger.error(
                f'Failed to load row from {table_name}: '
                f'{type(e).__name__} - {e}'
            )
            return []

    def save(
        self,
        database_name: str,
        table_name: str,
        columns: dict,
        rows: list,
        drop: bool
    ) -> None:
        try:
            with self._db_session(database_name) as cursor:
                if drop:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

                query_to_check = (
                    'SELECT name FROM sqlite_master '
                    'WHERE type="table" AND name=?'
                )
                cursor.execute(query_to_check, (table_name,))
                
                if not cursor.fetchone():
                    column_defs = [
                        f'"{col}" {dtype}' for col, dtype in columns.items()
                    ]
                    query_to_create = (
                        f'CREATE TABLE "{table_name}" '
                        f'({", ".join(column_defs)})'
                    )
                    cursor.execute(query_to_create)

                query_to_insert = (
                    f'INSERT {"" if drop else "OR IGNORE"} '
                    f'INTO "{table_name}" '
                    f'VALUES ({", ".join(['?'] * len(columns))})'
                )
                cursor.executemany(query_to_insert, rows)
        except Exception as e:
            self.logger.error(
                f'Failed to save data into {table_name}: '
                f'{type(e).__name__} - {e}'
            )

    @contextmanager
    def _db_session(self, database_name: str):
        db_path = os.path.join(
            os.path.dirname(__file__), 'databases', database_name
        )
        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            yield cursor
            connection.commit()
        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()