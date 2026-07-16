"""Health endpoint schemas."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    app_name: str
    api_version: str
    engine_version: str
