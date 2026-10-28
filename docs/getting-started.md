# Getting started — local Q&A demo

The current milestone is an offline demo with simulated answers and sample citations. It does not ingest PDFs yet. See the [current handoff](changelog.md) for verified status and [restart investigation](RESTART_BRIEF.md) for history.

Use Python 3.11 and Node 20.19 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000. The home page offers demo Q&A; `/auth` has local mock sign-in, `/demo` an alternate Q&A view, `/quiz` simulated practice questions, and `/quest-map` static quests.

All frontend calls use `/api/backend`, forwarded by Next to `http://127.0.0.1:8000`. Override server-only `BACKEND_URL` before starting/building Next if needed; restart/rebuild after changing it. Compose supplies `http://backend:8000`. The older public frontend URL variables are no longer used. No credentials are required for the demo.

Health: `GET /health` returns `{"status":"ok"}`. Mock tokens `student_token` and `prof_token` produce stable identities; invalid credentials are rejected. These mocks are local-development behavior, not production identity verification.

```sh
# Root, activated venv
python -m pytest -q
bash backend/scripts/e2e_smoke.sh
BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh
```

The smoke commands require running servers. Logs default to `logs/app.json`; `RAGEDU_LOG_PATH` overrides the destination. Tests isolate logs in temporary directories.

Docker Compose is optional: `docker compose -f docker-compose.dev.yml up --build`. It also starts OpenSearch and LocalStack, which the current demo does not use. Full container startup has not been reverified in this restart pass. Review dependency advisories in the handoff before public hosting.
