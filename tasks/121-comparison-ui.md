# Task 121: Comparison UI

## Goal

Add frontend comparison workflow.

## Scope

- Select saved/current configurations.
- Select baseline.
- Configure rounds/seeds.
- Sortable/hideable comparison table.
- Delta charts.
- Export action.

## Out of Scope

- Batch UI.

## Functional Requirements

- Users can compare configurations and inspect absolute and relative metrics.

## Technical Requirements

- UI must disclose common-random-number limitations.

## Tests

- Comparison creation flow.
- Table sorting/column visibility.
- Export action smoke.

## Acceptance Criteria

- UI can compare two configs and show baseline deltas.

## Likely Files

- `frontend/src/features/comparisons/`
- `backend/src/blackjack_api/api/routes/comparisons.py`

## Risks

- Overstating fairness of comparisons with different rules.
