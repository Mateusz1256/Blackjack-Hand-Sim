"""SQLite connection helpers."""

from pathlib import Path
from sqlite3 import Connection
from sqlite3 import connect as sqlite_connect


def connect(database_path: str | Path) -> Connection:
    connection = sqlite_connect(str(database_path))
    connection.row_factory = None
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
