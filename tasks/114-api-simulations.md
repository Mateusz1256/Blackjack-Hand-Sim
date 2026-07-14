# Task 114: API Simulations

## Goal

Expose simulation execution and results through API endpoints.

## Scope

- Start simulation endpoint.
- Status endpoint.
- Result endpoint.
- Trace retrieval endpoint.
- Error mapping.

## Out of Scope

- Comparison and batch endpoints.
- Frontend UI.

## Functional Requirements

- API clients can validate, start, monitor, and fetch simulation results.

## Technical Requirements

- Request handlers must enqueue heavy work instead of running it inline.

## Tests

- Endpoint happy paths.
- Validation errors.
- Simulation failure mapping.

## Acceptance Criteria

- API returns a complete report for a short deterministic simulation.

## Likely Files

- `backend/src/blackjack_api/api/routes/simulations.py`
- `backend/src/blackjack_api/schemas/`
- `backend/tests/`

## Risks

- Leaking internal tracebacks to API clients.
