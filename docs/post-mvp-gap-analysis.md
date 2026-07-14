# Post-MVP Gap Analysis

## Current Architecture

The current project is a single Python package under `src/blackjack_simulator`.
It contains a deterministic blackjack engine, YAML configuration loading, CLI
entry points, report renderers, tests, and example configs. The domain engine is
still independent from CLI, output formatting, and file formats.

Module map:

- `cards`, `hand`, `shoe`: rank-only card model, hand valuation, shoe shuffling,
  penetration, and deterministic RNG injection.
- `rules`: typed table-rule dataclasses plus legal-action helpers for dealer
  behavior, double, surrender, split, insurance, peek, and ENHC.
- `round`: single-round orchestration, player/dealer actions, insurance, split,
  double, surrender, ENHC, settlement handoff, and card counter observation.
- `settlement`: net-result settlement for main hands, insurance, blackjack
  payout, surrender, and ENHC loss variants.
- `engine`: multi-round orchestration, worker seed derivation, worker splitting,
  optional process execution, and statistics aggregation.
- `strategies`: S17/H17 basic strategy tables and insurance strategies.
- `betting`: flat, Martingale, Paroli, Fibonacci, D'Alembert, and true-count
  spread betting.
- `counting`: Hi-Lo running and true-count support.
- `statistics`: streaming collector, mergeable variance, drawdown, streaks, and
  final report model.
- `output`: console, JSON, and CSV report renderers.
- `configuration`: YAML-to-domain parsing and factory methods for shoes,
  strategies, counters, worker settings, and output settings.
- `cli`: `validate`, `run`, and compact `trace` commands.

## Public Interfaces

The main public interfaces are exported from `blackjack_simulator.__init__`:
domain models, rule dataclasses, strategies, counters, report helpers,
`run_simulation`, `run_worker_simulations`, worker seed helpers, and
`SimulationConfig`.

The CLI public surface is:

- `blackjack-simulator validate CONFIG [--rounds N] [--seed N] [--workers N]`
- `blackjack-simulator run CONFIG [--rounds N] [--seed N] [--workers N]`
- `blackjack-simulator trace CONFIG [--rounds N] [--seed N] [--workers N]`

## Available Features

- 1+ decks, penetration, shuffle-after-round, and deterministic seeds.
- S17/H17 dealer behavior.
- American hole-card peek and European no-hole-card.
- Blackjack payout variants through configuration.
- Hit, stand, double, split, surrender, insurance, and ENHC settlement.
- Basic strategy profiles for S17 and H17 with legal-action fallback.
- Insurance strategies: never, always, even money, and count-based in code.
- Betting systems: flat, Martingale, Paroli, Fibonacci, D'Alembert, and
  true-count spread, including YAML support for all of them.
- Hi-Lo running count and true count.
- Streaming statistics with merge support.
- JSON, CSV, and console reports.
- Deterministic multi-worker simulation helpers.
- YAML example configs and final validation tests.

## Missing Features vs Project V2

- No typed trace event model. Current CLI trace is only a compact text summary
  from retained `RoundResult` objects.
- No trace JSON output, trace filtering, event timeline, or web-ready trace
  schema.
- No audit module for card consistency, bankroll invariants, action legality,
  statistics consistency, determinism, or basic-strategy table checks.
- No configuration comparison service or CLI command.
- No batch simulation model for many independent sessions, percentiles, risk of
  ruin, or histogram data.
- No preset model, preset metadata, built-in preset catalog, or preset
  import/export.
- Counting is limited to Hi-Lo. There is no KO, Hi-Opt I/II, Omega II, true
  count rounding configuration, minimum deck denominator, or wonging.
- No strategy deviations, Illustrious 18, Fab 4, or conflict validation.
- Advanced betting is not present: bankroll percentage, Kelly, session limits,
  stop-loss, stop-win, and reset rules.
- No backend package, FastAPI app, API schemas, repositories, task queue,
  persistence, or async job lifecycle.
- No frontend package, configuration builder, results dashboard, comparison UI,
  batch UI, history, presets UI, accessibility tests, or E2E tests.
- Config import/export is YAML-only through files; no JSON import/export, schema
  versions, migration, unknown-field reporting, or preview.
- Report export is limited to one summary JSON/CSV shape; no report schema
  metadata, ZIP, PDF, chart image export, or chart data payloads.

## Technical Issues

- `round.play_round` directly executes game flow without an event sink, making
  post-facto detailed trace reconstruction difficult.
- `RoundResult` captures final hands and settlements but not intermediate
  decisions, fallback decisions, card-deal order metadata, shoe number, or
  bankroll transitions.
- `Shoe` does not expose shoe sequence number or shuffle events, which trace and
  audit need.
- Strategy decisions do not currently include rationale or the pre-fallback
  decision in a structured event.
- Configuration parsing is hand-written and permissive for unknown fields; V2
  requires strict unknown-field handling and schema versioning.
- Worker execution supports report aggregation but not progress reporting,
  cancellation, persistence, or per-worker trace/audit diagnostics.
- Statistics report lacks many V2 metrics such as win/loss/push rates,
  blackjack rate, surrender rate, split rate, double rate, dealer bust rate,
  confidence intervals, exposure, and ruin indicators.
- Current package layout has no `backend/` or `frontend/`; adding them should be
  incremental and should not move the existing engine package until there is a
  clear packaging reason.

## Test Gaps

- No trace event contract tests.
- No audit invariant tests.
- No comparison or batch tests.
- No strict config unknown-field tests.
- No API, persistence, task queue, frontend, accessibility, or E2E tests.
- Long-run testing exists as a validation config and short deterministic smoke;
  heavy million-round tests are not part of regular pytest, which is appropriate
  but should be documented in future release checks.

## Migration Risks

- Adding trace events inside `round.py` could accidentally change game order or
  counting behavior. Event emission must be side-effect-light and covered by
  regression tests.
- Strict config validation can break existing user configs if introduced
  without schema migration and clear errors.
- Batch and API execution can overrun local resources without configurable
  limits.
- Frontend and backend must not duplicate blackjack rules.
- Process-based worker execution requires picklable factories; future strategy
  factories must keep this constraint.
- Full trace for many rounds can become very large. Trace capture needs limits,
  filters, and storage policy before backend/UI integration.

## Recommended Order

1. Add typed trace events and an event collector without changing behavior.
2. Add CLI trace output and JSON trace export.
3. Add audit checks on top of trace and existing reports.
4. Add comparison and batch services before backend endpoints.
5. Add presets and strict configuration/schema handling.
6. Expand counting, deviations, and betting.
7. Add backend foundation, persistence, and task queue.
8. Add frontend foundation and feature UIs.
9. Add export formats, E2E, accessibility, Docker, and final validation.

## Keep Without Major Refactor

- Card, hand, rules, settlement, betting strategies, basic strategy tables,
  statistics collector, report model, output renderers, and current CLI commands.
- Existing domain package location under `src/blackjack_simulator`.
- Current unit and integration tests as regression coverage.

## Requires Refactor or Extension

- `round.play_round`: add optional event sink and structured decision metadata.
- `Shoe`: expose shuffle/shoe identifiers for trace and audit.
- `configuration`: add schema version, strict field validation, JSON support,
  migration hooks, and richer warnings.
- `statistics`: add event-derived outcome counters and confidence intervals.
- `engine`: expose progress hooks and session-level metadata for batch/backend.
- Project layout: add `backend/`, `frontend/`, `presets/`, and `reports/`
  incrementally without moving engine code prematurely.
