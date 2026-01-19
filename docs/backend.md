# Backend Endpoints

The backend is a FastAPI application defined in `backend/app/main.py`. This page summarizes the key HTTP endpoints and how they are meant to be used.

## Health

### `GET /health`

- Returns either `{ "status": "ok" }` or `{ "ok": true }` depending on how tests invoke it.
- The implementation intentionally supports both shapes to keep the test suite stable.

Use this endpoint for lightweight “is the process up?” checks.

## Auth and identity demo

These endpoints exercise the mock auth model and are useful both for demos and tests.

- `GET /whoami`
  - Requires an `Authorization: Bearer <token>` header.
  - Returns the resolved role for the current request.
- `GET /greeting`
  - Without auth: returns a message for an anonymous user.
  - With auth: progresses from “student” to “professor” across calls to demonstrate role changes.
- `GET /protected/student`
  - Requires role `student`.
- `GET /protected/professor`
  - First authed call returns 403 (treated as `student`), second returns 200 as `professor`.
- `GET /protected/auth`
  - Requires any authenticated user.

The underlying logic and mock tokens are implemented in `backend/app/auth.py` and exercised heavily in `backend/tests/test_auth.py` and `backend/tests/test_main.py`.

## RAG

### `POST /rag/answer`

- Request body:
  - `{"query": "..."}` **or** `{"question": "..."}`
  - Optional: `top_k` (int), `course_id` (string)
- Response body (happy path):

  ```json
  {
    "answer": "ANSWER based on retrieved docs: ...",
    "citations": [
      {"title": "Doc 1", "page": 1, "snippet": "Context A", "score": 0.9}
    ],
    "metadata": {
      "top_k": 5,
      "course_id": null,
      "confidence": 0.9
    }
  }
  ```

- Response when the guardrail fires:
  - `answer` is a generic “Not enough context” message.
  - `citations` is an empty list.
  - `metadata.confidence` is `0.0`.

Implementation details:

- Input validation and logging live in `backend/app/main.py`.
- The RAG core (`answer_query`) and guardrail logic live in `backend/app/rag.py`.

## Quiz APIs

These endpoints implement a minimal quiz flow, mainly for demonstration and testing.

- `POST /quiz/generate`
  - Input: `{ "query": "topic", "num_questions": 5 }` (with bounds on `num_questions`).
  - Output: `{ "quiz_id": "...", "questions": [...] }` where each question includes choices and an answer.
- `POST /quiz/submit`
  - Input: `{ "quiz_id": "...", "user_id": "...", "results": [{"id": "q1", "correct": true}, ...] }`.
  - Output: `{ "ok": true, "score": <correct>, "total": <len(results)> }`.

---

!!! info "Where to edit"
    Source: `docs/backend.md`  
    Routes: `backend/app/main.py`  
    Tests: `backend/tests/test_main.py`, `backend/tests/test_rag_answer.py`
