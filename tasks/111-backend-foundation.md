# Task 111: Backend Foundation

## Goal

Create FastAPI backend foundation around the existing engine.

## Scope

- Backend package scaffold.
- FastAPI app factory.
- Health endpoint.
- Shared settings.
- OpenAPI metadata.
- Test setup.

## Out of Scope

- Persistence.
- Long-running task queue.
- Frontend.

## Functional Requirements

- Backend starts and exposes health check.

## Technical Requirements

- Backend must call engine through public interfaces.
- Blackjack rules must not be duplicated.

## Tests

- App import.
- Health endpoint.
- OpenAPI availability.

## Acceptance Criteria

- `pytest` includes backend health tests.

## Likely Files

- `backend/`
- `pyproject.toml`
- `tests` or `backend/tests`

## Risks

- Packaging complexity in a repo that currently has one Python package.
