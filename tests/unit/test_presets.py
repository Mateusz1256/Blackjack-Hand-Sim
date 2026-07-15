from pathlib import Path

from blackjack_simulator.configuration import AppConfig
from blackjack_simulator.presets import (
    export_preset,
    get_builtin_preset,
    import_preset,
    list_builtin_presets,
    load_preset_config,
    preset_from_yaml,
    preset_to_yaml,
)


def test_builtin_presets_have_required_count_and_are_valid() -> None:
    presets = list_builtin_presets()

    assert len(presets) >= 10
    assert len({preset.metadata.id for preset in presets}) == len(presets)
    for preset in presets:
        assert preset.metadata.source == "built-in"
        assert preset.metadata.read_only is True
        assert isinstance(load_preset_config(preset), AppConfig)


def test_get_builtin_preset_by_id() -> None:
    preset = get_builtin_preset("standard-6d-s17")

    assert preset.metadata.name == "Standard 6 Deck S17"
    assert preset.configuration["rules"]["decks"] == 6
    assert preset.configuration["rules"]["dealer"]["hits_soft_17"] is False


def test_preset_yaml_roundtrip() -> None:
    preset = get_builtin_preset("european-no-hole-card")

    imported = preset_from_yaml(preset_to_yaml(preset))

    assert imported.to_dict() == preset.to_dict()


def test_preset_file_import_export_roundtrip(tmp_path: Path) -> None:
    preset = get_builtin_preset("single-deck-three-to-two")
    path = tmp_path / "preset.yaml"

    export_preset(preset, path)
    imported = import_preset(path)

    assert imported.to_dict() == preset.to_dict()
