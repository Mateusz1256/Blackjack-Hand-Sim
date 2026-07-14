# Agent Instructions

## Working Rules

- Before changing code, read `README.md`, `docs/architecture.md`, and the active
  task file.
- Do not implement functionality outside the active task without a clear reason.
- Do not change domain behavior without a test.
- Every bug fix must include a regression test.
- Do not remove existing tests only to make the pipeline pass.
- Do not change public interfaces without updating documentation.
- Preserve deterministic behavior for fixed seeds.

## Quality Gates

Run these commands before finishing a task:

```powershell
pytest
ruff check .
ruff format --check .
mypy src
```

If the commands change because project configuration changes, update this file
and `README.md`.

## Commit Scope

Each commit should be small, coherent, and describable in one sentence. Include
tests appropriate for the change.

Do not combine unrelated refactors, new features, documentation changes, and
mass formatting in one commit.

Use Conventional Commits, for example:

- `chore: configure project foundation`
- `feat: add dealer soft 17 behavior`
- `fix: prevent blackjack payout after split`
- `test: add ace valuation coverage`

## Blackjack Rule Assumptions

If a blackjack rule is uncertain:

1. Do not guess silently.
2. Record the assumption in documentation.
3. Make the rule configurable when common variants exist.
4. Add a test for the chosen behavior.
