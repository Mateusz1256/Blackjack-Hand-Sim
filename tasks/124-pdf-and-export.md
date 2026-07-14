# Task 124: PDF and Export

## Goal

Add complete export support for reports and charts.

## Scope

- JSON report schema with metadata.
- Multi-file CSV export.
- ZIP export.
- PDF report generation.
- Chart image export.

## Out of Scope

- Email/share workflows.

## Functional Requirements

- Users can export simulation, comparison, and batch reports.

## Technical Requirements

- PDF must be a structured report, not a screenshot dump.

## Tests

- JSON schema.
- CSV file set.
- PDF smoke.
- ZIP contents.

## Acceptance Criteria

- A completed report can be exported in JSON, CSV/ZIP, and PDF.

## Likely Files

- `backend/src/blackjack_api/services/export_service.py`
- `frontend/src/features/export/`

## Risks

- PDF dependencies increasing install complexity.
