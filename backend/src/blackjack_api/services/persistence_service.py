"""Persistence service entry points."""

from pathlib import Path
from sqlite3 import Connection

from blackjack_api.repositories import connect, migrate


def open_database(database_path: str | Path) -> Connection:
    connection = connect(database_path)
    migrate(connection)
    return connection
