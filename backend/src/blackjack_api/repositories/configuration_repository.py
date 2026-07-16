"""Repository for persisted simulator configurations."""

from dataclasses import dataclass
from datetime import UTC, datetime
from sqlite3 import Connection, IntegrityError
from uuid import uuid4

from blackjack_simulator.configuration import parse_app_config


@dataclass(frozen=True, slots=True)
class ConfigurationRecord:
    id: str
    name: str
    config_text: str
    created_at: str
    updated_at: str


class ConfigurationRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, *, name: str, config_text: str) -> ConfigurationRecord:
        parse_app_config(config_text)
        now = _now()
        record = ConfigurationRecord(
            id=str(uuid4()),
            name=name,
            config_text=config_text,
            created_at=now,
            updated_at=now,
        )
        try:
            self._connection.execute(
                """
                INSERT INTO configurations
                    (id, name, config_text, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.name,
                    record.config_text,
                    record.created_at,
                    record.updated_at,
                ),
            )
        except IntegrityError as exc:
            msg = f"configuration already exists: {name}"
            raise ValueError(msg) from exc
        self._connection.commit()
        return record

    def get(self, configuration_id: str) -> ConfigurationRecord | None:
        row = self._connection.execute(
            """
            SELECT id, name, config_text, created_at, updated_at
            FROM configurations
            WHERE id = ?
            """,
            (configuration_id,),
        ).fetchone()
        if row is None:
            return None
        return ConfigurationRecord(*row)

    def get_by_name(self, name: str) -> ConfigurationRecord | None:
        row = self._connection.execute(
            """
            SELECT id, name, config_text, created_at, updated_at
            FROM configurations
            WHERE name = ?
            """,
            (name,),
        ).fetchone()
        if row is None:
            return None
        return ConfigurationRecord(*row)

    def delete(self, configuration_id: str) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM configurations WHERE id = ?",
            (configuration_id,),
        )
        self._connection.commit()
        return cursor.rowcount > 0


def _now() -> str:
    return datetime.now(UTC).isoformat()
