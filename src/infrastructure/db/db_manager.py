from __future__ import annotations
from contextlib import contextmanager
from logging import getLogger
from os.path import dirname, join
from sqlite3 import connect


logger = getLogger(__name__)


class DBManager():
    """
    A class for managing SQLite database operations such as fetching
    and saving data, with built-in error handling and logging.
    """

    def fetch_all(self, database_name: str, table_name: str) -> list:
        """
        Retrieve all rows from the specified table
        in the given SQLite database.

        If the table does not exist, an empty list is returned.

        Args:
            database_name: Name of the database file
            table_name: Name of the table to fetch data from

        Returns:
            list: A list of rows from the table, or an empty list on failure
        """

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
            logger.error(
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
        """
        Retrieve a single row from the specified table where the key column
        matches the provided key value.

        If the table or row does not exist, an empty list is returned.

        Args:
            database_name: Name of the database file
            table_name: Name of the table to query
            key_column: Column name used as a key
            key_value: Value to match in the key column

        Returns:
            list: The matched row as a list, or an empty list on failure
        """

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
            logger.error(
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
        """
        Save multiple rows into the specified table in the SQLite database.

        If the table does not exist, it will be created using the provided
        column definitions. Optionally drops the table before inserting.

        Args:
            database_name: Name of the database file
            table_name: Name of the table to save data into
            columns: Dictionary mapping column names to SQLite types
            rows: List of rows (tuples) to be inserted
            drop: If True, the table will be dropped before insertion
        """

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
            logger.error(
                f'Failed to save data into {table_name}: '
                f'{type(e).__name__} - {e}'
            )

    @contextmanager
    def _db_session(self, database_name: str):
        """
        Internal context manager for handling database connections
        and transactions safely.

        Commits the transaction if successful, otherwise rolls back.

        Args:
            database_name: Name of the database file

        Yields:
            sqlite3.Cursor: Cursor object for executing SQL commands
        """

        db_path = join(dirname(__file__), 'databases', database_name)
        connection = None
        cursor = None

        try:
            connection = connect(db_path)
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