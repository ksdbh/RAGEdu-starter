# RAGEdu — course-grounded study companion

RAGEdu (called **EduRAG** in older documentation) helps students find answers in instructor-provided course materials and inspect page citations. Quiz and syllabus/quest screens remain prototypes.

**Current state — October 30, 2026:** a text PDF can be ingested locally and searched from the web UI, with real document/page citations. This offline path uses **keyword retrieval and verbatim source excerpts**, not semantic embeddings or LLM synthesis. An explicitly labeled simulated demo remains the default.

See the [changelog and current handoff](docs/changelog.md) for completed tasks, verification, and next steps. The [original restart investigation](docs/RESTART_BRIEF.md) preserves historical findings, rather than current setup instructions.

## Set up

Use Python 3.11 and Node **24.15+** (the `.nvmrc` selects the 24.x line). CI uses Python 3.11 and current Node 24; local verification used Python 3.13.5 and Node 24.22.2. SQLite must include FTS5 support (standard in the verified environments).

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
cd frontend
npm ci
cd ..
```

## Search a real PDF

From the repository root with the venv active:

```sh
# Included synthetic two-page PDF; substitute your own text PDF when ready.
python -m backend.app.ingest backend/examples/graphs.pdf --course CS101
# Equivalent helper: make ingest FILE=backend/examples/graphs.pdf COURSE=CS101

RAGEDU_MODE=local python -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend
npm run dev
```

Open http://localhost:3000, select **CS101**, and ask **What does Dijkstra require?** You should see matching excerpts from `graphs.pdf`, page 1, describing nonnegative edge weights. `/demo` uses the same course-aware UI.

The default corpus lives at `data/courses.sqlite3`, excluded from Git. Use `--index /path/to/corpus.sqlite3` for the CLI and `RAGEDU_INDEX_PATH=/path/to/corpus.sqlite3` for the API to change it. Run root commands from the same directory or use an absolute path. Reimporting identical PDF bytes into the same course replaces its passages without duplicates; changed bytes create a separate document. Imported materials are visible to the running API immediately; reload the page to refresh its course list.

Only text PDFs are supported: no OCR for image-only scans, no encrypted PDFs, and a 25 MiB file-size limit. This is a trusted local ingestion tool, not an untrusted upload service. Course selection scopes retrieval; it is **not authorization**. No document-download endpoint or cloud sync is provided. No keys, AWS credentials, or external model calls are needed.

## Run the simulated demo

Start the API without `RAGEDU_MODE=local`:

```sh
python -m uvicorn backend.app.main:app --reload --port 8000
```

The UI labels answers and sample sources as simulated. Other prototype routes: `/auth` (mock sign-in), `/quiz`, and `/quest-map`. Quiz scores and quest progress are not persisted.

## Verify changes

```sh
# Root, with the venv active
python -m pytest -q

# Frontend
cd frontend
npm ci
npm test
npm run typecheck
npm run build
npm audit
```

With both servers running, from root:

```sh
# For a backend started in default demo mode:
bash backend/scripts/e2e_smoke.sh
BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh

# For local mode with the included sample PDF already ingested:
EXPECTED_MODE=local COURSE_ID=CS101 bash backend/scripts/e2e_smoke.sh
EXPECTED_MODE=local COURSE_ID=CS101 BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh
```

The sample smoke query is `Dijkstra Astar` and expects two passages; set `SMOKE_QUERY` for a different corpus. `GET /rag/status` reports the mode, retrieval/generation type, and local course counts. `GET /health` returns `{"status":"ok"}`.

## Configuration and architecture

| Setting | Purpose |
| --- | --- |
| `RAGEDU_MODE` | API `demo` (default) or `local`; invalid values return an unavailable error, never a demo fallback. |
| `RAGEDU_INDEX_PATH` | Local SQLite corpus, default `data/courses.sqlite3`; same path as CLI `--index`. |
| `RAGEDU_LOG_PATH` | Request log destination, default `logs/app.json`; log errors do not fail Q&A. |
| `BACKEND_URL` | Server-only Next proxy destination, default `http://127.0.0.1:8000`. Set before starting/building Next and restart/rebuild after changing it. |

All frontend API calls use the same-origin `/api/backend` proxy. Old public frontend URL variables are superseded. Compose supplies `http://backend:8000` and defaults to the simulated demo; host-ingested files are not automatically mounted into containers.

- `frontend/components/Study.tsx`: course selection, question flow, honest mode/empty/error states, and source citations shared by `/` and `/demo`.
- `backend/app/ingest.py`: actual PDF CLI plus bounded character chunking; `local_index.py`: durable FTS5 keyword retrieval filtered by course.
- `backend/app/study.py`: explicit local/demo runtimes; `main.py`: API routes; `rag.py`: evidence guardrails, prompt orchestration, and citation metadata.
- `backend/app/auth.py`: token-aware local mock identity; real Cognito remains unimplemented. Local study routes are not access-controlled.
- `backend/app/db.py`, `quests.py`: separate scaffold helpers for course/syllabus/progress work.
- `infra/terraform/`: AWS scaffolding, not a deployed application. OpenSearch/LocalStack and hash-embedding helpers are not used by the local keyword path.

The frontend now uses Next 16.4.3/React 19.3.1; the October 30 npm audit reports zero vulnerabilities, including development dependencies. That is a point-in-time package audit, not a production security review. No cloud application deployment was performed.

## Where to resume

Choose representative course materials/questions and evaluate retrieval: the current keyword search can miss paraphrases and returns excerpts rather than explanations. Decide whether the next slice needs semantic embeddings, an LLM provider, and AWS/OpenSearch. Preserve course isolation and the insufficient-evidence behavior. See [next acceptance criteria](docs/changelog.md) before extending quizzes, progress storage, or deployment.
