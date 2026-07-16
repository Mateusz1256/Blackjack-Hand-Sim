"""SQLite schema migrations."""

from sqlite3 import Connection

SCHEMA_VERSION = 1


def migrate(connection: Connection) -> None:
    current_version = connection.execute("PRAGMA user_version").fetchone()[0]
    if current_version > SCHEMA_VERSION:
        msg = f"database schema version {current_version} is newer than supported"
        raise RuntimeError(msg)
    if current_version == SCHEMA_VERSION:
        return

    _migrate_to_v1(connection)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()


def _migrate_to_v1(connection: Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS configurations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            config_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS presets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            config_text TEXT NOT NULL,
            read_only INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            configuration_id TEXT,
            run_type TEXT NOT NULL,
            status TEXT NOT NULL,
            seed INTEGER,
            rounds INTEGER,
            config_snapshot TEXT NOT NULL,
            result_json TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(configuration_id) REFERENCES configurations(id)
                ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at);
        CREATE INDEX IF NOT EXISTS idx_runs_configuration_id
            ON runs(configuration_id);
        """,
    )
