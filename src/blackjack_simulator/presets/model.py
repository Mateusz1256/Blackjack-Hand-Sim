"""Preset data models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PresetMetadata:
    id: str
    name: str
    description: str
    category: str
    tags: tuple[str, ...]
    source: str
    version: int
    read_only: bool = False

    def __post_init__(self) -> None:
        if not self.id:
            msg = "preset id must not be empty"
            raise ValueError(msg)
        if not self.name:
            msg = "preset name must not be empty"
            raise ValueError(msg)
        if self.version <= 0:
            msg = "preset version must be positive"
            raise ValueError(msg)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": list(self.tags),
            "source": self.source,
            "version": self.version,
            "read_only": self.read_only,
        }


@dataclass(frozen=True, slots=True)
class Preset:
    metadata: PresetMetadata
    configuration: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "configuration": self.configuration,
        }
