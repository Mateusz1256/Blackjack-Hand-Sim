"""Preset API schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PresetResponse(BaseModel):
    id: str
    name: str
    metadata: dict[str, Any]
    config_text: str
    read_only: bool
    created_at: str
    updated_at: str


class PresetListResponse(BaseModel):
    presets: list[PresetResponse]


class PresetImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset_text: str = Field(min_length=1)


class PresetDuplicateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
