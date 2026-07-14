# Task 107: Presets

## Goal

Add validated table-rule presets with metadata.

## Scope

- Preset model and metadata.
- Built-in preset catalog.
- Import/export of preset files.
- Read-only built-in preset behavior.

## Out of Scope

- Preset UI.
- Database persistence.

## Functional Requirements

- Users can list and load built-in presets.
- Presets are ordinary validated configurations plus metadata.

## Technical Requirements

- Built-in presets must avoid unverifiable real-casino claims.

## Tests

- Preset validation.
- Required built-in preset count.
- Import/export roundtrip.

## Acceptance Criteria

- At least ten built-in presets are available and valid.

## Likely Files

- `presets/`
- `src/blackjack_simulator/presets/`
- `tests/unit/test_presets.py`

## Risks

- Preset drift from supported config schema.
