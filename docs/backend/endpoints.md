# Backend endpoints

This page lists key backend endpoints and their contracts.

Where to edit

!!! info "Where to edit"
- Source: backend/app/main.py
- RAG orchestration: backend/app/rag.py
- Tests: backend/tests/

Endpoints (summary)

- GET /health
  - Purpose: basic liveness check
  - Response: 200 OK {"status": "ok"}
  - Where to change: backend/app/main.py

- GET /whoami
  - Purpose: return current user info (uses auth dependency)
  - Where to change: backend/app/auth.py

- POST /rag/answer
  - Purpose: answer a user query using retrieval + LLM synthesis
  - See API Contract below

API Contract: POST /rag/answer

Request schema (JSON):

```json
{
  "course_id": "CS101",
  "query": "Explain the chain rule",
  "top_k": 5,
  "temperature": 0.0,
  "max_tokens": 512
}
```

Validation rules

- course_id: required string
- query: required string, non-empty
- top_k: optional integer (default 5), 1 <= top_k <= 20
- temperature: optional float between 0.0 and 1.0

Response schema (JSON):

```json
{
  "answer": "...",
  "sources": [
    {"course_id": "CS101", "page": 12, "section": "Derivatives", "text": "..."}
  ],
  "meta": {"model": "openai-xyz", "latency_ms": 123}
}
```

Where to change the response generation

!!! info "Where to edit"
- Module: backend/app/rag.py
- Function: answer_query (or route handler for /rag/answer)
- Tests: backend/tests/test_rag.py (expected test name: test_rag_answer)

Example curl

```bash
curl -X POST http://localhost:8000/rag/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer student_token" \
  -d '{"course_id":"CS101","query":"What is gradient descent?"}'
```

Test references

- backend/tests/test_rag.py::test_rag_answer  <!-- TODO: create/verify test file and test name -->
