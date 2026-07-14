# Task 113: Task Queue

## Goal

Add asynchronous simulation task execution.

## Scope

- Local task queue abstraction.
- Worker process/service.
- Job status and progress model.
- Cancellation.

## Out of Scope

- Frontend progress UI.
- Redis production deployment if local queue is sufficient initially.

## Functional Requirements

- Long simulations do not run directly in request handlers.
- Jobs can be queried and cancelled.

## Technical Requirements

- Progress updates must be bounded and not require per-round persistence.

## Tests

- Job lifecycle.
- Cancellation.
- Failure status.

## Acceptance Criteria

- A backend service can enqueue and complete a short simulation.

## Likely Files

- `backend/src/blackjack_api/workers/`
- `backend/src/blackjack_api/services/`
- `backend/tests/`

## Risks

- Race conditions in status updates.
