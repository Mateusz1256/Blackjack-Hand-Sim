# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses Semantic
Versioning.

## [Unreleased]

### Added

- YAML betting strategy configuration for flat, Martingale, Paroli, Fibonacci,
  D'Alembert, and true-count spread betting, including table limits.
- Typed trace event model and optional in-memory collector for round replay
  groundwork.
- CLI trace report rendering with event-type/feature filters and JSON export.
- Engine audit command with PASS/WARNING/FAIL/SKIPPED checks and strict mode.
- Configuration comparison service and CLI with baseline deltas plus JSON/CSV
  export.
- Batch simulation service and CLI with deterministic session seeds,
  final-bankroll percentiles, risk-of-ruin, and JSON/CSV export.
- Validated built-in table-rule presets with metadata and YAML import/export.
- Advanced counting systems for KO, Hi-Opt I, Hi-Opt II, and Omega II with
  configurable true-count rounding, minimum deck denominator, and initial
  running count.
- Count-based basic-strategy deviations with built-in Illustrious 18/Fab 4
  sets, custom YAML rules, priority conflict checks, and legal-action fallback.

## [1.0.0] - 2026-07-14

### Added

- Project foundation with Python packaging, linting, formatting, typing, tests,
  documentation, task plan, and CI configuration.
- Card and hand domain primitives with ace valuation, soft/hard hand detection,
  blackjack detection, bust detection, and pair detection.
- Deterministic shoe generation with deck count, penetration tracking, injected
  RNG shuffling, and S17/H17 dealer drawing behavior.
- Basic round flow with hit, stand, blackjack, bust, push, flat betting,
  bankroll updates, and net-result settlement.
- Table-driven basic strategy profiles for S17 and H17 with hard, soft, and
  pair tables plus legal-action fallback.
- Double and surrender rules with action legality, double bet settlement, early
  surrender, late surrender, and basic-strategy fallback integration.
- Split rules with resplit limits, split ace restrictions, double-after-split
  checks, multi-hand round settlement, and post-split blackjack handling.
- Insurance side-bet settlement, always/never/even-money insurance strategies,
  and American dealer peek behavior.
- European no-hole-card dealer flow with `all_bets` and `original_bet_only`
  settlement variants for dealer blackjack after player actions.
- Progressive betting systems for Martingale, Paroli, Fibonacci, and
  D'Alembert, plus table limits and insufficient-bankroll handling.
- Hi-Lo card counting with running/true count, reveal-timed round integration,
  count-based insurance, and true-count betting spread.
- Streaming statistics collector with Welford variance, house edge, RTP,
  drawdown, streaks, and JSON/CSV/console report output helpers.
- YAML configuration loading and CLI commands for validate, run, and trace with
  basic seed/round overrides.
- Deterministic worker simulation helpers with worker seed derivation, round
  splitting, multiprocessing support, and statistics collector merging.
- MVP validation assets with H17, 6:5 blackjack, ENHC, and million-round example
  configurations.
