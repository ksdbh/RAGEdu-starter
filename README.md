# RAGEdu — course-grounded study companion

RAGEdu (called **EduRAG** in older documentation) is intended to help students ask questions about instructor-provided course materials and inspect source citations. It also includes quiz and syllabus/quest prototypes.

**Current state — October 28, 2026:** the local Q&A demo builds and runs without AWS credentials or paid APIs. Its answers and sample sources are simulated. Real PDF ingestion, semantic retrieval, durable course data, and production identity are not connected yet.

Start with the [current handoff and eight completed tasks](docs/changelog.md). The [restart investigation](docs/RESTART_BRIEF.md) preserves the original repository findings, historical recovery candidates, and product questions; its opening update distinguishes the repaired demo from that original baseline.

## Run the local demo

Use Python 3.11 and Node 20.19 or newer. Local verification used Python 3.13.5 and Node 24.12.0; CI is configured for Python 3.11/Node 20.19.0.

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000. Ask a question to see a **demo answer** with sample page/snippet citations. Other routes: `/auth`, `/demo`, `/quiz`, `/quest-map`.

All UI requests go through the same-origin `/api/backend` proxy. Next.js forwards them to `http://127.0.0.1:8000` by default. To change the backend, set server-only `BACKEND_URL` before starting or building Next.js. Older `NEXT_PUBLIC_BACKEND_URL`/`NEXT_PUBLIC_API_URL` setup instructions are superseded. No CORS configuration or API key is needed for the demo.

## Verify changes

```sh
# Root, with the venv activated. Logs are isolated in temporary test directories.
python -m pytest -q

# Frontend
cd frontend
npm ci
npm test
npm run typecheck
npm run build
```

With both servers running, from the root:

```sh
bash backend/scripts/e2e_smoke.sh
BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh
```

Health has one response: `GET /health` → `{"status":"ok"}`. Request logs default to `logs/app.json`; override with `RAGEDU_LOG_PATH`. Logging errors do not fail Q&A requests.

## Architecture and limits

- `frontend/`: Next.js App Router Q&A and quiz; Pages Router `/auth`, `/demo`, `/quest-map`. A committed lockfile and TypeScript/Vitest setup provide reproducible frontend checks.
- `backend/app/main.py`: FastAPI routes. Q&A still explicitly selects demo search/generation clients and returns `metadata.mode: "demo"`.
- `backend/app/rag.py`: retrieval orchestration and citations. Empty, failed, unusable, or low-score retrieval returns insufficient evidence without calling the LLM. Selected context and citations obey `top_k`.
- `backend/app/auth.py`: token-aware local mock identity. `student_token` and `prof_token` select stable roles; invalid credentials cannot access protected routes. Cognito verification remains unimplemented. Mock auth is for local development.
- `backend/app/ingest.py`: chunking/hash-embedding/index-mapping helpers, **not a functioning ingest CLI**. Historical ingestion code can be reviewed before rebuilding; see the restart brief.
- `backend/app/db.py`, `quests.py`: in-memory course helpers and deterministic syllabus-to-quest transforms, not wired into the user journey. Quiz scores and quest progress are not persisted.
- `infra/terraform/`: AWS scaffolding, not an application deployment. Compose optionally starts OpenSearch/LocalStack; the demo does not use those services.

The [developer docs](https://ksdbh.github.io/RAGEdu-starter/) contain architecture intentions as well as implementation details. Consult this README, changelog, tests, and code for current behavior.

## Where to resume

Next milestone: **one real course document → searchable passages → a question → an answer citing actual pages**, with offline tests and an honest insufficient-evidence path. Review historical parsing/indexing implementations before replacing them. See [next tasks and acceptance criteria](docs/changelog.md).

A production-dependency audit still reports critical Next.js and high PostCSS advisories in the retained Next 14 line. This session's patch update is not a complete security migration; evaluate a supported Next.js release before any public deployment. No cloud application deployment was performed.
