"""Simulation API schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SimulationStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_text: str = Field(min_length=1)
    configuration_id: str | None = None


class JobProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current: int
    total: int
    message: str


class SimulationJobResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: str
    progress: JobProgressResponse
    error: str | None = None


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
