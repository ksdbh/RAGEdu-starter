from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_quiz_generate_defaults():
    payload = {"query": "graph algorithms"}
    resp = client.post("/quiz/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "quiz_id" in data
    assert "questions" in data
    assert len(data["questions"]) == 5

    # Check structure of a question
    q = data["questions"][0]
    assert "id" in q
    assert "type" in q
    assert q["type"] in ("mcq", "short")
    assert "prompt" in q
    assert "answer" in q
    assert "distractors" in q
    assert "spaced_rep" in q


def test_quiz_generate_custom_num():
    payload = {"query": "shortest path", "num_questions": 3}
    resp = client.post("/quiz/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["questions"]) == 3


def test_quiz_submit_bad_request():
    # Missing results should be rejected
    payload = {"quiz_id": "abc", "user_id": "u1", "results": []}
    resp = client.post("/quiz/submit", json=payload)
    assert resp.status_code == 400
