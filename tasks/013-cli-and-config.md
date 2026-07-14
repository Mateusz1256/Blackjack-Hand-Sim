# Task 013: CLI and Configuration

## Goal

Add validated YAML configuration and CLI commands.

## Scope

- YAML loading.
- Validation.
- `run`.
- `validate`.
- `trace`.
- Parameter overrides.

## Out of Scope

- Web API.

## Functional Requirements

- User can run a full simulation from a YAML file.
- Invalid config produces a clear message.

## Technical Requirements

- CLI must call the domain engine through stable service functions.

## Tests

- Valid config.
- Invalid config.
- CLI smoke tests.
- Override behavior.

## Acceptance Criteria

- Config-driven simulation works end to end.

## Likely Files

- `src/blackjack_simulator/configuration.py`
- `src/blackjack_simulator/cli/main.py`
- `configs/*.yaml`
- `tests/integration/test_cli.py`

## Risks

- Letting YAML format leak into domain models.
