# Task 125: E2E and Accessibility

## Goal

Add end-to-end and accessibility coverage.

## Scope

- Playwright setup.
- Main user flows.
- Keyboard navigation checks.
- Basic accessibility assertions.
- Loading/error/empty states.

## Out of Scope

- Full manual accessibility audit.

## Functional Requirements

- Critical workflows are covered from browser perspective.

## Technical Requirements

- E2E tests must use short deterministic simulations.

## Tests

- Create config.
- Run simulation.
- Open results.
- Export JSON.
- Import config.
- Compare configs.
- Run batch.

## Acceptance Criteria

- E2E suite passes locally and in CI.

## Likely Files

- `frontend/tests/`
- `playwright.config.*`
- `.github/workflows/ci.yml`

## Risks

- Flaky tests from asynchronous job timing.
