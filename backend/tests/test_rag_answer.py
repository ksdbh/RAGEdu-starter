import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def request_log(tmp_path, monkeypatch):
    from backend.app import main
    path = tmp_path / "logs" / "app.json"
    monkeypatch.setattr(main, "LOG_PATH", path)
    return path


def test_empty_question_returns_400():
    resp = client.post("/rag/answer", json={"question": "   "})
    assert resp.status_code == 400
    assert "non-empty" in resp.json().get("detail", "").lower()


def test_too_long_question_returns_400():
    long_q = "x" * 1001
    resp = client.post("/rag/answer", json={"question": long_q})
    assert resp.status_code == 400
    assert "too long" in resp.json().get("detail", "").lower()


def test_success_creates_structured_log_and_returns_answer(request_log):
    resp = client.post("/rag/answer", json={"question": "What is 2+2?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "stubbed answer" in body["answer"].lower()
    # ensure structured log file exists and contains at least one JSON line
    assert request_log.exists()
    with open(request_log, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    assert len(lines) >= 1
    entry = json.loads(lines[-1])
    assert entry.get("route") == "/rag/answer"
    assert entry.get("status") == "ok"


def test_unwritable_log_does_not_break_answer(tmp_path, monkeypatch):
    from backend.app import main
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("occupied")
    monkeypatch.setattr(main, "LOG_PATH", blocked / "app.json")
    response = client.post("/rag/answer", json={"query": "What is RAG?"})
    assert response.status_code == 200
    assert response.json()["answer"]
