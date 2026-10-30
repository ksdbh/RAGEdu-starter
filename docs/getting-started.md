# Getting started — local course search

As of October 30, RAGEdu can ingest a real text PDF and return matching course excerpts with page citations. This uses keyword search, not semantic retrieval or model synthesis. The default simulated demo is still available. See the [current handoff](changelog.md) for exact verification.

Use Python 3.11 and Node 24.15+ (`.nvmrc` selects Node 24). From root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m backend.app.ingest backend/examples/graphs.pdf --course CS101
RAGEDU_MODE=local python -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000, choose CS101, and ask “What does Dijkstra require?” Citations should identify `graphs.pdf`, page 1. `/demo` uses the same UI; `/auth`, `/quiz`, and `/quest-map` remain mock/prototype screens. To use the simulated demo, start the API without `RAGEDU_MODE=local`.

The index defaults to root `data/courses.sqlite3`, ignored by Git. The CLI `--index` and API `RAGEDU_INDEX_PATH` must point to the same file. All frontend calls use the same-origin `/api/backend` proxy, forwarded to `http://127.0.0.1:8000` by default; server-only `BACKEND_URL` changes it before Next startup/build. No credentials or API calls are required.

See the [local PDF search guide](guides/local-course-search.md) for supported PDF types, atomic reimports, isolation boundaries, HTTP contract, and failure behavior. No course authorization or production upload service is implemented.

```sh
# Root, activated venv
python -m pytest -q
EXPECTED_MODE=local COURSE_ID=CS101 bash backend/scripts/e2e_smoke.sh
EXPECTED_MODE=local COURSE_ID=CS101 BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh
```

Smoke checks require both servers and the sample PDF corpus. Frontend checks: `npm test`, `npm run typecheck`, `npm run build`, `npm audit`. Tests isolate request logs; runtime logs default to `logs/app.json` and can be changed with `RAGEDU_LOG_PATH`.

Docker Compose remains optional and defaults to the simulated demo. It starts OpenSearch/LocalStack too, but neither is used by local SQLite retrieval, and host index files are not automatically mounted. Full container startup has not been reverified in this pass.
