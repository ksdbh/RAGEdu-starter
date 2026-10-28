#!/usr/bin/env bash
set -euo pipefail

# No files or credentials needed. Can target FastAPI or the Next.js proxy.
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PYTHON="${PYTHON:-python3}"
"$PYTHON" - "$BASE_URL" <<'PYTHON'
import json
import sys
from urllib.request import Request, urlopen

base = sys.argv[1].rstrip("/")

def request(path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=15) as response:
        return json.load(response)

assert request("/health") == {"status": "ok"}, "Unexpected health contract"
answer = request("/rag/answer", {"query": "Compare Dijkstra and A*", "top_k": 2})
assert answer.get("answer"), "Missing answer"
assert len(answer["citations"]) == 2, "Expected exactly top_k sample citations"
assert all(c.get("title") and c.get("snippet") and c.get("page") for c in answer["citations"])
assert answer["metadata"]["mode"] == "demo", "Expected explicit demo mode"
print("Smoke passed: health, demo answer, and source citations at " + base)
PYTHON
