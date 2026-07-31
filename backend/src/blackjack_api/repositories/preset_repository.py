"""Repository for persisted preset snapshots."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from sqlite3 import Connection
from typing import Any

from blackjack_simulator.presets import preset_from_yaml, preset_to_yaml
from blackjack_simulator.presets.model import Preset


@dataclass(frozen=True, slots=True)
class PresetRecord:
    id: str
    name: str
    metadata_json: str
    config_text: str
    read_only: bool
    created_at: str
    updated_at: str

    def metadata(self) -> dict[str, Any]:
        loaded = json.loads(self.metadata_json)
        if not isinstance(loaded, dict):
            msg = "preset metadata must decode to an object"
            raise ValueError(msg)
        return loaded

    def preset(self) -> Preset:
        return preset_from_yaml(self.config_text)


class PresetRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def upsert(self, preset: Preset) -> PresetRecord:
        config_text = preset_to_yaml(preset)
        now = _now()
        existing = self.get(preset.metadata.id)
        created_at = existing.created_at if existing is not None else now
        record = PresetRecord(
            id=preset.metadata.id,
            name=preset.metadata.name,
            metadata_json=json.dumps(preset.metadata.to_dict()),
            config_text=config_text,
            read_only=preset.metadata.read_only,
            created_at=created_at,
            updated_at=now,
        )
        self._connection.execute(
            """
            INSERT INTO presets
                (
                    id, name, metadata_json, config_text, read_only,
                    created_at, updated_at
                )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                metadata_json = excluded.metadata_json,
                config_text = excluded.config_text,
                read_only = excluded.read_only,
                updated_at = excluded.updated_at
            """,
            (
                record.id,
                record.name,
                record.metadata_json,
                record.config_text,
                int(record.read_only),
                record.created_at,
                record.updated_at,
            ),
        )
        self._connection.commit()
        return record

    def get(self, preset_id: str) -> PresetRecord | None:
        row = self._connection.execute(
            """
            SELECT
                id, name, metadata_json, config_text, read_only, created_at,
                updated_at
            FROM presets
            WHERE id = ?
            """,
            (preset_id,),
        ).fetchone()
        if row is None:
            return None
        return PresetRecord(
            id=row[0],
            name=row[1],
            metadata_json=row[2],
            config_text=row[3],
            read_only=bool(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def list(
        self,
        *,
        category: str | None = None,
        include_read_only: bool = True,
    ) -> list[PresetRecord]:
        clauses: list[str] = []
        if not include_read_only:
            clauses.append("read_only = 0")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"""
            SELECT
                id, name, metadata_json, config_text, read_only, created_at,
                updated_at
            FROM presets
            {where}
            ORDER BY read_only DESC, name ASC
            """,
        ).fetchall()
        records = [
            PresetRecord(
                id=row[0],
                name=row[1],
                metadata_json=row[2],
                config_text=row[3],
                read_only=bool(row[4]),
                created_at=row[5],
                updated_at=row[6],
            )
            for row in rows
        ]
        if category:
            return [
                record
                for record in records
                if str(record.metadata().get("category", "")) == category
            ]
        return records

    def delete(self, preset_id: str) -> bool:
        existing = self.get(preset_id)
        if existing is None:
            return False
        if existing.read_only:
            msg = f"cannot delete read-only preset: {preset_id}"
            raise ValueError(msg)
        cursor = self._connection.execute(
            "DELETE FROM presets WHERE id = ?",
            (preset_id,),
        )
        self._connection.commit()
        return cursor.rowcount > 0


def _now() -> str:
    return datetime.now(UTC).isoformat()
