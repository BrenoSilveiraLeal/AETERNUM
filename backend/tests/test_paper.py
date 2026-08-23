from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_paper_order_is_simulated():
    response = client.post("/api/paper/orders", json={"symbol": "AAPL", "side": "BUY", "quantity": 2, "rationale": "Scenario test"})
    assert response.status_code == 201
    assert response.json()["status"] == "SIMULATED"
    assert response.json()["mode"] == "PAPER"
