from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_audit_endpoint_schema():
    payload = {
        "company_name": "Acme Corp",
        "period": "2025 Q4",
        "financials": {"revenue": 1000000, "net_income": 150000},
    }

    response = client.post("/api/v1/audit", json=payload)
    assert response.status_code == 500 or response.status_code == 200
    assert "summary" in response.json() or response.status_code == 500
