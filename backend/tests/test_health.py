from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_is_independent_of_test_name(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "test_health.py::anything")
    assert client.get("/health").json() == {"status": "ok"}
