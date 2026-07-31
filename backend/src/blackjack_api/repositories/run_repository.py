"""Repository for persisted run metadata."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from sqlite3 import Connection
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class RunRecord:
    id: str
    configuration_id: str | None
    run_type: str
    status: str
    seed: int | None
    rounds: int | None
    config_snapshot: str
    result_json: str | None
    created_at: str
    updated_at: str

    def result(self) -> dict[str, Any] | None:
        if self.result_json is None:
            return None
        loaded = json.loads(self.result_json)
        if not isinstance(loaded, dict):
            msg = "run result must decode to an object"
            raise ValueError(msg)
        return loaded


class RunRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(
        self,
        *,
        run_type: str,
        status: str,
        config_snapshot: str,
        configuration_id: str | None = None,
        seed: int | None = None,
        rounds: int | None = None,
        result: dict[str, Any] | None = None,
    ) -> RunRecord:
        now = _now()
        record = RunRecord(
            id=str(uuid4()),
            configuration_id=configuration_id,
            run_type=run_type,
            status=status,
            seed=seed,
            rounds=rounds,
            config_snapshot=config_snapshot,
            result_json=json.dumps(result) if result is not None else None,
            created_at=now,
            updated_at=now,
        )
        self._connection.execute(
            """
            INSERT INTO runs
                (
                    id, configuration_id, run_type, status, seed, rounds,
                    config_snapshot, result_json, created_at, updated_at
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.configuration_id,
                record.run_type,
                record.status,
                record.seed,
                record.rounds,
                record.config_snapshot,
                record.result_json,
                record.created_at,
                record.updated_at,
            ),
        )
        self._connection.commit()
        return record

    def get(self, run_id: str) -> RunRecord | None:
        row = self._connection.execute(
            """
            SELECT
                id, configuration_id, run_type, status, seed, rounds,
                config_snapshot, result_json, created_at, updated_at
            FROM runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return RunRecord(*row)

    def list(
        self,
        *,
        run_type: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[RunRecord]:
        if limit <= 0:
            msg = "limit must be positive"
            raise ValueError(msg)
        clauses: list[str] = []
        params: list[str | int] = []
        if run_type:
            clauses.append("run_type = ?")
            params.append(run_type)
        if status:
            clauses.append("status = ?")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"""
            SELECT
                id, configuration_id, run_type, status, seed, rounds,
                config_snapshot, result_json, created_at, updated_at
            FROM runs
            {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
        return [RunRecord(*row) for row in rows]

    def delete(self, run_id: str) -> bool:
        cursor = self._connection.execute(
            "DELETE FROM runs WHERE id = ?",
            (run_id,),
        )
        self._connection.commit()
        return cursor.rowcount > 0


def _now() -> str:
    return datetime.now(UTC).isoformat()
