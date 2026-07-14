# Task 117: Configuration Builder

## Goal

Build a comprehensive frontend configuration form.

## Scope

- Sections for simulation, bankroll, rules, shoe, strategy, counting, betting,
  output, deviations, and batch-related fields.
- Dynamic betting strategy fields.
- Local validation and backend validation integration.
- Warning summary.

## Out of Scope

- Running simulations UI.
- Preset management UI.

## Functional Requirements

- Users can edit all engine-supported config options from the UI.

## Technical Requirements

- Frontend validation must mirror backend schemas without duplicating game logic.

## Tests

- Component tests for field dependencies.
- Validation states.
- Betting preview sequence.

## Acceptance Criteria

- UI can produce a valid config accepted by backend validation.

## Likely Files

- `frontend/src/features/configuration/`
- `backend/src/blackjack_api/schemas/configuration.py`

## Risks

- Form covering only a subset of supported engine options.
