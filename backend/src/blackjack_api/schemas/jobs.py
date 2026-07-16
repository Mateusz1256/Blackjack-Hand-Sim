"""Shared job response schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class JobProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current: int
    total: int
    message: str


class JobResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: str
    progress: JobProgressResponse
    error: str | None = None


class JobResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str
    status: str
    result: dict[str, Any]
