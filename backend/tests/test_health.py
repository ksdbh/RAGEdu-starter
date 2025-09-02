from fastapi.testclient import TestClient

# Import app from the most common locations used in this repo when running
# pytest from the backend/ directory or from the repository root.
try:
    # when running `cd backend && pytest`
    from app.main import app
except Exception:
    # when running from project root or other contexts
    from backend.app.main import app  # type: ignore

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
