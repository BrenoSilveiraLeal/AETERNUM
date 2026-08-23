from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_integrations_do_not_claim_private_connections():
    statuses = {item["name"]: item["status"] for item in client.get("/api/integrations/status").json()}
    assert statuses["Open Finance"] == "NOT_CONFIGURED"
    assert statuses["B3 licenciada"] == "DISABLED"
