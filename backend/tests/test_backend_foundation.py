from fastapi.testclient import TestClient

from blackjack_api.config import BackendSettings
from blackjack_api.main import create_app


def test_backend_app_imports() -> None:
    app = create_app()

    assert app.title == "Blackjack Simulator API"


def test_health_endpoint() -> None:
    app = create_app(
        BackendSettings(
            app_name="Test API",
            version="test",
            environment="test",
        ),
    )
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "Test API",
        "api_version": "test",
        "engine_version": "1.0.0",
    }


def test_openapi_is_available() -> None:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "Blackjack Simulator API"
    assert "/api/v1/health" in payload["paths"]
