# Task 120: Results Dashboard

## Goal

Create a results dashboard for simulation reports.

## Scope

- Overview metric cards.
- Bankroll, outcomes, betting, risk, rules, trace, and raw data tabs.
- Chart data downsampling strategy.
- Trace link integration.

## Out of Scope

- PDF export.
- Comparison dashboard.

## Functional Requirements

- Users can inspect summary metrics, charts, tables, rules, and raw report data.

## Technical Requirements

- Large chart datasets must be aggregated or virtualized.

## Tests

- Dashboard render.
- Tab navigation.
- Empty/error states.

## Acceptance Criteria

- A completed simulation report is usable from the dashboard.

## Likely Files

- `frontend/src/features/results/`
- `frontend/src/components/charts/`

## Risks

- Rendering too many points in the browser.
