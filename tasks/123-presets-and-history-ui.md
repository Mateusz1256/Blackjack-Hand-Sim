# Task 123: Presets and History UI

## Goal

Add UI for presets and run history.

## Scope

- Preset listing, load, duplicate, import, export.
- History filters.
- Re-run, compare, export, delete actions.
- Confirmation dialogs.

## Out of Scope

- User accounts.

## Functional Requirements

- Users can manage presets and revisit previous runs.

## Technical Requirements

- Built-in presets are read-only.

## Tests

- Preset load/duplicate flow.
- History filtering.
- Delete confirmation.

## Acceptance Criteria

- Saved run can be opened and re-run from history.

## Likely Files

- `frontend/src/features/presets/`
- `frontend/src/features/history/`
- `backend/src/blackjack_api/api/routes/presets.py`

## Risks

- Accidental deletion without confirmation.
