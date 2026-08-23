from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_is_paper():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["trading_mode"] == "PAPER"


def test_aurion_is_seeded():
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert response.json()[0]["unique_id"] == "AURION"
