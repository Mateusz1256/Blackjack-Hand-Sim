# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses Semantic
Versioning.

## [Unreleased]

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
