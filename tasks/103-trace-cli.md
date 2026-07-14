# Task 103: Trace CLI

## Goal

Expose typed trace events through CLI reports and JSON export.

## Scope

- Richer `trace` command output.
- `--json-file` or config-driven trace JSON output.
- Event filtering by type and selected round features.

## Out of Scope

- Web timeline.
- Audit report.

## Functional Requirements

- Users can inspect readable trace output for selected rounds.
- Users can export raw trace events to JSON.

## Technical Requirements

- CLI must use the trace event model from Task 102.
- Output must not require storing trace for unrelated rounds.

## Tests

- CLI trace smoke tests.
- JSON shape tests.
- Filter tests.

## Acceptance Criteria

- `blackjack-simulator trace CONFIG --rounds N` prints structured details and
  can export JSON.

## Likely Files

- `src/blackjack_simulator/cli/main.py`
- `src/blackjack_simulator/output/`
- `tests/integration/test_cli.py`

## Risks

- Trace output becoming too noisy for terminal use.
