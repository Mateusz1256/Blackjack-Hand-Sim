"""Run history API schemas."""

from pydantic import BaseModel


class RunHistoryRecordResponse(BaseModel):
    id: str
    configuration_id: str | None
    run_type: str
    status: str
    seed: int | None
    rounds: int | None
    config_snapshot: str
    created_at: str
    updated_at: str


class RunHistoryListResponse(BaseModel):
    runs: list[RunHistoryRecordResponse]
