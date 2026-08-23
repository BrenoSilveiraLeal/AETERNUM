from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_requires_configured_ai_without_fabricating_response():
    response = client.post("/api/chat", json={"message": "Qual é meu saldo?"})
    assert response.status_code == 200
    assert any(text in response.json()["message"] for text in ("não está configurada", "temporariamente indisponível"))


def test_dashboard_lists_only_active_agents():
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert all(agent["status"] == "ACTIVE" for agent in response.json())
