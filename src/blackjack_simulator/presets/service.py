"""Preset import/export and validation services."""

from pathlib import Path
from typing import Any, cast

import yaml

from blackjack_simulator.configuration import AppConfig, parse_app_config
from blackjack_simulator.presets.catalog import builtin_presets
from blackjack_simulator.presets.model import Preset, PresetMetadata


def list_builtin_presets() -> tuple[Preset, ...]:
    return builtin_presets()


def get_builtin_preset(preset_id: str) -> Preset:
    for preset in builtin_presets():
        if preset.metadata.id == preset_id:
            return preset
    msg = f"unknown built-in preset: {preset_id}"
    raise KeyError(msg)


def load_preset_config(preset: Preset) -> AppConfig:
    return parse_app_config(yaml.safe_dump(preset.configuration, sort_keys=False))


def validate_preset(preset: Preset) -> None:
    load_preset_config(preset)


def import_preset(path: str | Path) -> Preset:
    return preset_from_yaml(Path(path).read_text(encoding="utf-8"))


def export_preset(preset: Preset, path: str | Path) -> None:
    Path(path).write_text(preset_to_yaml(preset), encoding="utf-8")


def preset_to_yaml(preset: Preset) -> str:
    return yaml.safe_dump(preset.to_dict(), sort_keys=False)


def preset_from_yaml(text: str) -> Preset:
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        msg = "preset file must contain a mapping"
        raise ValueError(msg)

    metadata = _metadata_from_mapping(_mapping(raw.get("metadata"), "metadata"))
    configuration = _mapping(raw.get("configuration"), "configuration")
    preset = Preset(metadata=metadata, configuration=configuration)
    validate_preset(preset)
    return preset


def _metadata_from_mapping(data: dict[str, Any]) -> PresetMetadata:
    tags_raw = data.get("tags", ())
    tags: tuple[str, ...]
    if tags_raw is None:
        tags = ()
    elif isinstance(tags_raw, list):
        tags = tuple(str(tag) for tag in tags_raw)
    else:
        msg = "metadata.tags must be a list"
        raise ValueError(msg)

    return PresetMetadata(
        id=str(_required(data, "id", "metadata.id")),
        name=str(_required(data, "name", "metadata.name")),
        description=str(data.get("description", "")),
        category=str(data.get("category", "custom")),
        tags=tags,
        source=str(data.get("source", "custom")),
        version=_positive_int(data.get("version", 1), "metadata.version"),
        read_only=bool(data.get("read_only", False)),
    )


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        msg = f"{field_name} must be a mapping"
        raise ValueError(msg)
    return cast("dict[str, Any]", value)


def _required(data: dict[str, Any], key: str, field_name: str) -> object:
    value = data.get(key)
    if value in (None, ""):
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value


def _positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        msg = f"{field_name} must be an integer"
        raise ValueError(msg)
    try:
        parsed = int(str(value))
    except ValueError as exc:
        msg = f"{field_name} must be an integer"
        raise ValueError(msg) from exc
    if parsed <= 0:
        msg = f"{field_name} must be positive"
        raise ValueError(msg)
    return parsed
