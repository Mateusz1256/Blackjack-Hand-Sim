# Docker Compose Deployment

The local Docker setup starts the browser UI, FastAPI backend, and a worker
container using safe development defaults.

```powershell
docker compose up --build
```

Open the panel at `http://localhost:8080`. The backend health endpoint is
available at `http://localhost:8000/api/v1/health`.

## Services

- `frontend`: builds the Vite app and serves static files through Nginx. The
  Nginx config proxies `/api/` to the backend service.
- `backend`: runs `uvicorn blackjack_api.main:app` on port `8000`.
- `worker`: uses the backend image and verifies the shared SQLite volume. The
  current task queue is intentionally local to the API process, so background
  jobs run in the backend container until a distributed queue is introduced.

## Environment

The compose defaults set:

```text
BLACKJACK_API_ENVIRONMENT=compose
BLACKJACK_API_DATABASE_PATH=/data/blackjack_api.sqlite3
```

SQLite data is stored in the named volume `blackjack-data`. Remove it with
`docker compose down -v` when you want a clean local database.

## Common Commands

```powershell
docker compose up --build
docker compose ps
docker compose logs -f backend
docker compose logs -f worker
docker compose down
```
