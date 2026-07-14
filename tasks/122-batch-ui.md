# Task 122: Batch UI

## Goal

Add frontend workflow for batch simulations.

## Scope

- Batch setup form.
- Progress and cancellation.
- Histograms and percentile charts.
- Best/worst session table.
- Risk-of-ruin view.

## Out of Scope

- PDF export.

## Functional Requirements

- Users can run and inspect many independent sessions.

## Technical Requirements

- Batch history must be sampled and visualized efficiently.

## Tests

- Batch form validation.
- Progress states.
- Result chart rendering smoke.

## Acceptance Criteria

- UI can run a small batch and show distribution metrics.

## Likely Files

- `frontend/src/features/batches/`
- `backend/src/blackjack_api/api/routes/batches.py`

## Risks

- Large batch reports overwhelming browser memory.
