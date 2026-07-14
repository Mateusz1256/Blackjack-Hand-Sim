# Task 119: Simulation Execution UI

## Goal

Add frontend workflow for starting and monitoring simulations.

## Scope

- Run button and job creation.
- Progress/status display.
- Cancel action.
- Error presentation.
- Link to results.

## Out of Scope

- Full results dashboard.
- Batch UI.

## Functional Requirements

- Users can run a simulation from the current config and monitor progress.

## Technical Requirements

- UI must not block while backend job runs.

## Tests

- Start flow.
- Progress states.
- Cancel flow.
- Error state.

## Acceptance Criteria

- A short simulation can be launched and opened from the UI.

## Likely Files

- `frontend/src/features/simulations/`
- `backend/src/blackjack_api/api/routes/simulations.py`

## Risks

- Poor cancellation feedback for already-finished jobs.
