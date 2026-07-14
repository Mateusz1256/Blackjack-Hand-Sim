# Task 118: Config Import and Export

## Goal

Add robust YAML and JSON import/export for configurations.

## Scope

- YAML import.
- JSON import.
- Preview and diff against current config.
- Schema version field.
- Migration hooks.
- Export full or changed-only config.

## Out of Scope

- Preset catalog UI.

## Functional Requirements

- Users can import pasted text or files and see validation results before apply.

## Technical Requirements

- Unknown fields must be reported, not ignored.
- No code execution from config input.

## Tests

- YAML/JSON roundtrip.
- Unknown field reporting.
- Migration smoke.

## Acceptance Criteria

- A config can be imported, previewed, applied, and exported.

## Likely Files

- `src/blackjack_simulator/configuration.py`
- `backend/src/blackjack_api/services/configuration_service.py`
- `frontend/src/features/configuration/`

## Risks

- Breaking existing configs during strict validation rollout.
