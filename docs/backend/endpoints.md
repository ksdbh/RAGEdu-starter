# Backend Endpoints — Reference

This reference lists the main backend HTTP endpoints and their contracts. Keep this document in sync with backend/app/main.py and backend/app/rag.py.

Common headers

- Authorization: Bearer <token> (supports mock tokens in dev)

Endpoints

1) GET /health

- Purpose: Health check
- Response: 200 OK with JSON {"status": "ok"}
- Where to change: backend/app/main.py

2) GET /whoami

- Purpose: Return current user info (mock or real Cognito)
- Response schema: {"sub": "string", "username": "string", "role": "string", "email": "string?"}
- Where to change: backend/app/auth.py::get_current_user

3) POST /rag/answer

- Purpose: Answer a user question grounded in course materials using retrieval + LLM.

API Contract: /rag/answer

Request schema (JSON):

{
  "course_id": "string",   # required — which course corpus to query
  "question": "string",    # required — user question
  "top_k": 5,               # optional — number of retrieved passages (default 5)
  "max_tokens": 512         # optional — LLM generation limit
}

Response schema (JSON):

{
  "answer": "string",
  "sources": [
    {"text": "string", "page": 1, "section": "string", "score": 0.95}
  ],
  "llm_raw": { /* provider-specific raw response */ }
}

Validation rules

- course_id: non-empty string.
- question: min length 3 characters.
- top_k: integer 1..20.
- max_tokens: integer > 0 and <= 2048 (provider-dependent).

Example curl

```bash
curl -X POST http://localhost:8000/rag/answer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer student_token" \
  -d '{"course_id":"CS101","question":"What is a RAG system?","top_k":3}'
```

Where to change implementation

!!! info "Where to edit"
    Source: docs/backend/endpoints.md
    Public contract: docs/backend/endpoints.md#raganswer
    Implementation: backend/app/rag.py :: answer_query (or similar)
    Route registration: backend/app/main.py
    Tests: backend/tests/test_rag.py (if present)

Tests

- Add unit tests that assert validation rules and that the /rag/answer route calls the retrieval pipeline and returns the expected schema.

<!-- TODO: If backend/app/rag.py does not exist, create a minimal implementation and tests. -->
