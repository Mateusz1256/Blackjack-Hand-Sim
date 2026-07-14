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
