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
    # Ensure the stubbed answer is returned exactly (keeps behavior explicit)
    assert data["answer"] == "This is a stub. Retrieval and LLM will be wired in subsequent PRs."
    assert isinstance(data["answer"], str)
    assert data["citations"] == []
    assert isinstance(data["metadata"], dict)
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


def test_rag_answer_empty_query_invalid():
    # query must be non-empty (min_length=1)
    payload = {"query": "", "top_k": 2}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 422


def test_rag_answer_defaults_when_omitted():
    # top_k and course_id are optional; top_k should default to 5
    payload = {"query": "What is a binary tree?"}
    resp = client.post("/rag/answer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata"]["top_k"] == 5
    assert data["metadata"]["course_id"] is None
