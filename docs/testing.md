# Testing

The current [handoff](changelog.md) records 64 backend and 8 frontend DOM tests, TypeScript/build/audit checks, and live direct/proxy smoke in both local and demo modes. No real-browser visual/hydration check is implied by DOM tests.

EduRAG relies on `pytest` tests under `backend/tests` to lock in the behavior of key endpoints and RAG primitives.

## What the tests guarantee

- **Health checks**
  - `/health` always responds with `{ "status": "ok" }`, independent of caller/test name.
- **Auth & greeting**
  - Mock tokens map to predictable roles (student/professor).
  - The greeting and protected endpoints enforce role requirements deterministically.
- **RAG behavior**
  - The prompt for the LLM includes a `Sources:` line.
  - Happy path: answers start with `"ANSWER based on"` and include normalized citations.
  - Guardrail path: when retrieval is empty, fails, has unusable passages, or similarity is too low, the LLM is **not** called (enforced via a `NeverLLM` test double).
- **Quiz APIs**
  - Quiz generation respects bounds on `num_questions`.
  - Quiz submission returns consistent scoring.

Full details and individual test conventions are in `docs/testing/overview.md` and `docs/testing/test-conventions.md`.

## Running tests locally

From the repo root using the Makefile:

```bash
make backend-test
```

Or directly with `pytest`:

```bash
python -m pytest -q
```

If you are running inside the Docker Compose CI stack you can also execute tests in the `backend` container:

```bash
docker compose -f docker-compose.ci.yml exec -T backend pytest -q
```

Frontend checks: `cd frontend`, then `npm ci`, `npm test`, `npm run typecheck`, and `npm run build`. See the [current handoff](changelog.md) for exact results and verification gaps.

## Adding new tests

When you extend the backend:

- Prefer small, focused tests under `backend/tests/`.
- Follow the naming patterns in `docs/testing/test-conventions.md`.
- Keep tests deterministic (e.g., rely on stub LLMs and embedding implementations rather than external services).

---

!!! info "Where to edit"
    Source: `docs/testing.md`  
    Tests: `backend/tests/`  
    How to run: `docs/testing/how-to-run.md`
