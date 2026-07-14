# Task 001: Project Foundation

## Goal

Create the package foundation without implementing blackjack game logic.

## Scope

- Directory structure.
- `pyproject.toml`.
- pytest, ruff, and mypy configuration.
- README, AGENTS, CHANGELOG, LICENSE.
- Architecture documentation.
- Task files.
- CI pipeline.
- Minimal package import test.

## Out of Scope

- Card, hand, shoe, round, settlement, strategy, betting, statistics, and CLI
  implementation.

## Functional Requirements

- The package can be installed in editable mode.
- The package can be imported.

## Technical Requirements

- Python 3.12+.
- No runtime dependencies.
- Tooling configured in `pyproject.toml`.

## Tests

- Smoke test importing `blackjack_simulator`.

## Acceptance Criteria

- `pytest` passes.
- `ruff check .` passes.
- `ruff format --check .` passes.
- `mypy src` passes.

## Likely Files

- `pyproject.toml`
- `src/blackjack_simulator/__init__.py`
- `tests/unit/test_package_import.py`
- project documentation and CI files

## Risks

- Adding game logic too early.
- Overcommitting to public APIs before the domain model exists.
