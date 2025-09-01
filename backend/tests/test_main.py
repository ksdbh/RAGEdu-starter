from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_rag_answer_defaults():
    payload = {"query": "What is unit testing?"}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["answer"].startswith("This is a stub")
    assert data["citations"] == []
    assert data["metadata"]["top_k"] == 5
    assert data["metadata"]["course_id"] is None


def test_rag_answer_with_course_and_topk():
    payload = {"query": "Explain Dijkstra", "course_id": "cs101", "top_k": 3}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata"]["top_k"] == 3
    assert data["metadata"]["course_id"] == "cs101"


def test_rag_answer_invalid_topk():
    payload = {"query": "x", "top_k": 0}
    resp = client.post("/rag/answer", json=payload)
    # Validation should reject top_k < 1
    assert resp.status_code == 422


def test_rag_answer_empty_query():
    payload = {"query": ""}
    resp = client.post("/rag/answer", json=payload)
    # Validation should reject empty query (min_length=1)
    assert resp.status_code == 422
