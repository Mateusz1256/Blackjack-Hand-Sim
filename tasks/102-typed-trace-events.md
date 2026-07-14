# Task 102: Typed Trace Events

## Goal

Add a typed trace event model and collector without changing game behavior.

## Scope

- Event dataclasses or typed records.
- Sequential event numbering.
- Round, hand, shoe, card, action, settlement, and bankroll fields.
- In-memory collector.
- JSON-serializable representation.

## Out of Scope

- CLI formatting.
- Web UI.
- Audit checks.

## Functional Requirements

- A simulation can emit structured events for a round.
- Events preserve order and contain enough metadata for later replay.

## Technical Requirements

- Event emission must be optional.
- Domain behavior must remain deterministic with and without tracing.

## Tests

- Event model serialization.
- Collector ordering.
- No-trace behavior matches existing round results.

## Acceptance Criteria

- Trace events can be collected for at least hit, stand, deal, settlement, and
  round start/end.

## Likely Files

- `src/blackjack_simulator/trace/`
- `src/blackjack_simulator/round.py`
- `tests/unit/test_trace.py`

## Risks

- Trace hooks changing card order or strategy behavior.
