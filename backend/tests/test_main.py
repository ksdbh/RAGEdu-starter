from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_rag_answer_success():
    payload = {"query": "What is RAG?", "top_k": 3, "course_id": "cs101"}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert data["citations"] == []
    assert data["metadata"]["top_k"] == 3
    assert data["metadata"]["course_id"] == "cs101"


def test_rag_answer_invalid_top_k():
    # top_k must be >= 1
    payload = {"query": "Hello", "top_k": 0}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 422


def test_rag_answer_missing_query():
    # query is required and must be non-empty
    payload = {"top_k": 2}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 422
