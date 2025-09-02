# Backend Endpoints

## `GET /health`
- Returns `{"status": "ok"}`.
- There is also an alias in some tests that expect `{"ok": true}`; the app handles both.

## Auth/Greeting demo
- `GET /whoami` – returns role for authorized requests.
- `GET /greeting` – demonstrates anonymous → student → professor progression across calls.
- `GET /protected/student` – requires `student`.
- `GET /protected/professor` – requires `professor`.
- `GET /protected/auth` – requires any authorized role.

## RAG
- `POST /rag/answer`
  - Request: `{"query": "..."}` or `{"question": "..."}` with optional `top_k`, `course_id`.
  - Response: `{"answer": "...", "citations": [...], "metadata": {"top_k": ..., "course_id": ..., "confidence": ...}}`

## Quiz
- `POST /quiz/generate` – demo question generator.
- `POST /quiz/submit` – simple scoring.