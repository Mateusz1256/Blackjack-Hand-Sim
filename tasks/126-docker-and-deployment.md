# Task 126: Docker and Deployment

## Goal

Provide local Docker Compose deployment.

## Scope

- Backend container.
- Frontend container.
- Worker container.
- Redis or local queue dependency if needed.
- SQLite or database volume.
- Environment documentation.

## Out of Scope

- Cloud-specific deployment.

## Functional Requirements

- `docker compose up` starts a usable local app.

## Technical Requirements

- Defaults must be safe for local development.

## Tests

- Build smoke.
- Health endpoint in compose environment.

## Acceptance Criteria

- User can open the panel after starting compose.

## Likely Files

- `Dockerfile`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `docs/`

## Risks

- Divergence between local non-Docker and Docker configuration.
