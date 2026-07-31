from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from blackjack_api.config import BackendSettings
from blackjack_api.main import create_app

ROOT = Path(__file__).resolve().parents[2]


def test_compose_declares_local_app_services() -> None:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())

    services = compose["services"]
    assert {"backend", "frontend", "worker"}.issubset(services)
    assert services["backend"]["environment"]["BLACKJACK_API_DATABASE_PATH"] == (
        "/data/blackjack_api.sqlite3"
    )
    assert services["backend"]["volumes"] == ["blackjack-data:/data"]
    assert services["frontend"]["ports"] == ["8080:80"]
    assert services["worker"]["command"] == ["python", "-m", "blackjack_api.worker"]
    assert "blackjack-data" in compose["volumes"]


def test_dockerfiles_define_healthchecks() -> None:
    backend_dockerfile = (ROOT / "backend" / "Dockerfile").read_text()
    frontend_dockerfile = (ROOT / "frontend" / "Dockerfile").read_text()

    assert "HEALTHCHECK" in backend_dockerfile
    assert "http://127.0.0.1:8000/api/v1/health" in backend_dockerfile
    assert "HEALTHCHECK" in frontend_dockerfile
    assert "nginx" in frontend_dockerfile


def test_health_endpoint_uses_compose_settings(tmp_path: Path) -> None:
    app = create_app(
        BackendSettings(
            environment="compose",
            database_path=str(tmp_path / "compose.sqlite3"),
        ),
    )
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
