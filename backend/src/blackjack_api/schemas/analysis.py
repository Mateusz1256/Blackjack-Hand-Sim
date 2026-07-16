"""Comparison and batch API schemas."""

from pydantic import BaseModel, ConfigDict, Field


class ComparisonStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    configs: list[str] = Field(min_length=2)
    names: list[str] | None = None
    mode: str = "independent_seeds"
    rounds: int | None = None
    seed: int | None = None
    workers: int | None = None


class BatchStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_text: str = Field(min_length=1)
    sessions: int = Field(gt=0)
    rounds_per_session: int = Field(gt=0)
    base_seed: int | None = None
    configuration_id: str | None = None
