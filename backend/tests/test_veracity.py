from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_market_does_not_fabricate_values_when_unconfigured():
    payload = client.get("/api/market/history").json()
    assert payload["points"] == []
    assert "não configurada" in payload["data_status"]


def test_empty_portfolio_does_not_fabricate_positions():
    assert client.get("/api/portfolio/positions").json() == []
