#!/usr/bin/env bash
set -euo pipefail

# No files or credentials needed. Can target FastAPI or the Next.js proxy.
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PYTHON="${PYTHON:-python3}"
"$PYTHON" - "$BASE_URL" "${EXPECTED_MODE:-demo}" "${COURSE_ID:-}" "${SMOKE_QUERY:-Dijkstra Astar}" <<'PYTHON'
import json
import sys
from urllib.request import Request, urlopen

base = sys.argv[1].rstrip("/")
expected_mode, course, query = sys.argv[2:5]

def request(path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=15) as response:
        return json.load(response)

assert request("/health") == {"status": "ok"}, "Unexpected health contract"
assert request("/rag/status")["mode"] == expected_mode
payload = {"query": query, "top_k": 2}
if expected_mode == "local":
    assert course, "COURSE_ID is required for local corpus smoke"
    payload["course_id"] = course
answer = request("/rag/answer", payload)
assert answer.get("answer"), "Missing answer"
assert len(answer["citations"]) == 2, "Expected exactly top_k sample citations"
assert all(c.get("title") and c.get("snippet") and c.get("page") for c in answer["citations"])
assert answer["metadata"]["mode"] == expected_mode, "Unexpected Q&A mode"
if expected_mode == "local":
    assert answer["metadata"]["generation"] == "source_excerpts"
    assert all(c.get("document_id") and c.get("source") and c.get("course_id") == course for c in answer["citations"])
print("Smoke passed: health, " + expected_mode + " response, and source citations at " + base)
PYTHON
