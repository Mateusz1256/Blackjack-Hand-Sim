# Task 115: API Comparisons and Batches

## Goal

Expose comparison and batch workflows through API endpoints.

## Scope

- Comparison endpoints.
- Batch endpoints.
- Export endpoints for comparison/batch reports.
- Status integration with task queue.

## Out of Scope

- Frontend pages.

## Functional Requirements

- API clients can run comparisons and batches asynchronously.

## Technical Requirements

- Large jobs must use task queue and persistence.

## Tests

- Comparison endpoint smoke.
- Batch endpoint smoke.
- Export shape tests.

## Acceptance Criteria

- API can return completed comparison and batch reports for small fixtures.

## Likely Files

- `backend/src/blackjack_api/api/routes/comparisons.py`
- `backend/src/blackjack_api/api/routes/batches.py`
- `backend/tests/`

## Risks

- Report schema divergence from CLI services.
