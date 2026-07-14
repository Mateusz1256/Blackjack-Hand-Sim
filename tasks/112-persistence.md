# Task 112: Persistence

## Goal

Add persistence for configurations, runs, presets, and history.

## Scope

- Storage schema.
- Repository interfaces.
- SQLite local default.
- Migration approach.

## Out of Scope

- User accounts.
- Distributed database deployment.

## Functional Requirements

- Backend can save and retrieve configurations and run metadata.

## Technical Requirements

- Stored results must include enough config data to reproduce runs.

## Tests

- Repository roundtrips.
- Migration smoke.
- Duplicate and delete behavior.

## Acceptance Criteria

- Saved configuration can be loaded and validated.

## Likely Files

- `backend/src/blackjack_api/repositories/`
- `backend/src/blackjack_api/services/`
- `backend/tests/`

## Risks

- Persisting incomplete config snapshots.
