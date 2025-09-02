import os
import json
import shutil
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

LOG_PATH = os.path.join(os.getcwd(), "logs", "app.json")


def setup_function(fn):
    # ensure clean logs dir before each test
    logs_dir = os.path.join(os.getcwd(), "logs")
    if os.path.exists(logs_dir):
        shutil.rmtree(logs_dir)


def teardown_function(fn):
    logs_dir = os.path.join(os.getcwd(), "logs")
    if os.path.exists(logs_dir):
        shutil.rmtree(logs_dir)


def test_empty_question_returns_400():
    resp = client.post("/rag/answer", json={"question": "   "})
    assert resp.status_code == 400
    assert "non-empty" in resp.json().get("detail", "").lower()


def test_too_long_question_returns_400():
    long_q = "x" * 1001
    resp = client.post("/rag/answer", json={"question": long_q})
    assert resp.status_code == 400
    assert "too long" in resp.json().get("detail", "").lower()


def test_success_creates_structured_log_and_returns_answer():
    resp = client.post("/rag/answer", json={"question": "What is 2+2?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "stubbed answer" in body["answer"].lower()
    # ensure structured log file exists and contains at least one JSON line
    assert os.path.exists(LOG_PATH)
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    assert len(lines) >= 1
    entry = json.loads(lines[-1])
    assert entry.get("route") == "/rag/answer"
    assert entry.get("status") == "ok"
