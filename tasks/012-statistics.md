# Task 012: Statistics and Reports

## Goal

Implement streaming statistics and report outputs.

## Scope

- Collector.
- Welford variance.
- House edge.
- RTP.
- Drawdown.
- Streaks.
- JSON.
- CSV.
- Console report.

## Out of Scope

- CLI config parsing unless needed for manual report invocation.

## Functional Requirements

- Statistics do not store every round.
- Counters and aggregate values remain consistent.

## Technical Requirements

- Support mergeable worker statistics later.

## Tests

- Incremental mean and variance.
- House edge denominator choices.
- Drawdown and streaks.
- JSON/CSV output shape.

## Acceptance Criteria

- Reported values match controlled fixtures.

## Likely Files

- `src/blackjack_simulator/statistics/`
- `src/blackjack_simulator/output/`

## Risks

- Using the wrong denominator for house edge.
