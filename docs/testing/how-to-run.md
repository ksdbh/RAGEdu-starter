# How to run tests

From repository root with backend production/development requirements installed:

```sh
python -m pytest -q
# or: make backend-test
```

Root `pytest.ini` establishes canonical `backend.app` imports. Request logs are isolated by pytest fixtures; tests do not delete developer log directories or call paid APIs.

From `frontend/`:

```sh
npm ci
npm test
npm run typecheck
npm run build
```

With backend/frontend running, root `bash backend/scripts/e2e_smoke.sh` verifies FastAPI; `BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh` verifies the Next proxy. See the [handoff](../changelog.md) for results and limits.
