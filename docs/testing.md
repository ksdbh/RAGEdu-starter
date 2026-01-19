**`docs/testing.md`**
```markdown
# Testing

We rely on `pytest` with contract-style tests in `backend/tests`.

Key expectations:
- `/health` returns a stable shape (the app supports both `{"status":"ok"}` and `{"ok":true}` needs).
- The greeting/auth endpoints enforce roles deterministically so tests are reliable.
- RAG tests assert:
  - Prompt contains a "Sources:" line.
  - Happy path: answer starts with `"ANSWER based on"` and includes 3 normalized citations.
  - Guardrail path: **no** LLM call (enforced by `NeverLLM` in tests).

Run locally:
```bash
docker compose -f docker-compose.ci.yml exec -T backend pytest -q