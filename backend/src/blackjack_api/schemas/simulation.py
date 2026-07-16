"""Simulation API schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from blackjack_api.schemas.jobs import JobResponse


class SimulationStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_text: str = Field(min_length=1)
    configuration_id: str | None = None


SimulationJobResponse = JobResponse


class SimulationResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: str
    result: dict[str, Any]


class SimulationTraceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    events: list[dict[str, Any]]


class ValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valid: bool
    rounds: int
    seed: int
    workers: int
