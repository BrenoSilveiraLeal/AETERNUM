from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def aurion_id() -> int:
    agents = client.get("/api/agents").json()
    return next(item["id"] for item in agents if item["unique_id"] == "AURION")


def test_hold_signal_is_persisted_but_cannot_execute():
    response = client.post("/api/signals", json={"agent_id": aurion_id(), "symbol": "PETR4", "action": "HOLD", "confidence": 0.75, "reason": "Apenas observação", "position_size": 0})
    assert response.status_code == 201
    assert response.json()["status"] == "RECEIVED"
    assert client.post(f"/api/signals/{response.json()['id']}/execute").status_code == 409


def test_buy_signal_without_verified_quote_is_blocked():
    response = client.post("/api/signals", json={"agent_id": aurion_id(), "symbol": "PETR4", "action": "BUY", "confidence": 0.8, "reason": "Teste de bloqueio", "position_size": 1, "stop_loss": 9, "take_profit": 12})
    assert response.status_code == 201
    execution = client.post(f"/api/signals/{response.json()['id']}/execute")
    assert execution.status_code == 200
    assert execution.json()["status"] == "BLOCKED"
