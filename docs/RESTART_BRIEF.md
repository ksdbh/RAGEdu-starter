# RAGEdu restart briefing

Inspected: **2026-10-28 (America/New_York)**. Baseline: `main`, commit `8093421d152233cfe9117594877cf6913a48af0b` (2026-01-19).

## Follow-up delivered on 2026-10-30

The [current handoff](changelog.md) now supersedes both the original baseline and the October 28 demo pass. The offline course path ingests actual text PDFs into a persistent SQLite keyword index and returns course-filtered source excerpts with real page citations. Next/React/test tooling was migrated; full npm audit reports zero vulnerabilities. Verified: 64 backend tests, 8 frontend DOM tests, production build/typecheck, and direct/proxy smoke in both modes. See the handoff for exact runtime/CI status and limits; semantic retrieval, model synthesis, authorization, and educational evaluation remain future work.

## Follow-up delivered on 2026-10-28

The eight-task restart pass restored the local demo after this investigation. See the [current handoff/changelog](changelog.md) and [README](https://github.com/ksdbh/RAGEdu-starter/blob/main/README.md) for current commands and results. Backend checks now pass 45 tests; frontend checks pass 3 tests, TypeScript, and production build. HTTP smoke checks pass directly and through the Next.js proxy. Mock auth is token-derived, health is stable, logs are portable, and empty/error retrieval no longer substitutes sources. Frontend home routing and dependency installation are repaired. Browser interaction and live CI results remain unverified; dependency security migration remains open.

**Everything below records the pre-repair baseline at `8093421`; it is retained as investigation/history, not a claim that the repaired issues remain open.**

## Purpose and evidence standard

The [README](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/README.md) calls the product **EduRAG**, while the repository, UI, and API use **RAGEdu**. Its stated audience is students asking questions about course materials and instructors supplying those materials and practice activities. The intended value is course-grounded answers with page citations; quizzes and syllabus-derived study quests extend that journey.

**Verified implementation:** this is a FastAPI/Next.js scaffold with tested helper functions and deterministic demos. It does not currently provide a connected document-to-answer journey. Architecture diagrams describe a destination more complete than the code. **Inference:** restoring a reliable local Q&A demonstration, then connecting one real document, is the shortest useful restart. Product priority and naming still need confirmation.

No AGENTS.md was found in the repository or applicable parent directories. Reviewed README, CONTRIBUTING, WARP guidance, architecture/platform tour, setup/testing/environment docs, RAG/data-model guides, deployment/operations notes, workflows, and implementation. No dedicated prior handoff was found; roadmap is in README and changelog only records the initial scaffold. Several newer guide pages explicitly remain outlines.

## Where development stopped

- Initial working tree was clean. Only local branch is `main`, equal to the locally recorded `origin/main`; no fetch was performed, so live remote status is unknown. No branch switching, reset, stash application, or implementation edits were performed.
- Latest work: `8093421` refined documentation/navigation; `2baaa83` overhauled the docs hub/platform tour; `478d966` added WARP guidance and adjusted development requirements, all 2026-01-19. Reflog supports this as the latest local development session.
- Latest substantive RAG code fix: `1cfd020` (2025-09-22), restoring signature tolerance and the NeverLLM guard. September 2 history repeatedly adjusts health, role progression, fake results, and guardrails to match tests. October commits focus on assistant workflow installation/caching. **Inference:** stabilization of tests/automation preceded the documentation work; no saved explicit next-feature decision was found.
- **Preserved stash:** `stash@{0}`, commit `8fc3d08`, dated 2025-09-02, “WIP on main: cbe5966 docs: fill missing pages with starters.” Its sole file is `docs/rag.md`; the patch explains signature tolerance, empty-result demo fallback, and guardrails. It is older documentation, not an unfinished ingestion feature.
- Many remote-tracking `origin/assistant/*` refs remain and are not direct ancestors of HEAD. Their subjects cover generated features and workflow fixes; non-ancestry alone does not mean the changes were never integrated (history contains PR/squash counterparts).
- Recovery candidates: `origin/assistant/1756770431537` / `d1999cb` contains PDF parsing, CLI, and bulk indexing; the main-history counterpart is `815a2fb` (#30). `origin/assistant/1756770750038` / `a02bc23` contains score normalization and recency/section reranking; counterpart `7d18f45` (#33). Current files lack much of this behavior. Review these versions and subsequent replacements, especially `36cdf84`, before selectively recovering anything. Do not blindly merge historical branches.

## Architecture and actual user journey

| Area | Current code and behavior |
| --- | --- |
| Web | [frontend/package.json](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/package.json): Next.js 14.2.5, React/React DOM 18.3.1. Both App Router and Pages Router exist. [app/layout.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/app/layout.tsx) loads minimal CSS; Tailwind is not configured. |
| Home Q&A | [app/page.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/app/page.tsx) posts `{query, top_k}` to `NEXT_PUBLIC_API_URL + /rag/answer`; displays answer and citation objects. [pages/index.js](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/pages/index.js) also owns `/`, causing a build conflict. |
| Other screens | [pages/demo.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/pages/demo.tsx) loads [Demo.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/components/Demo.tsx); it reads top-level confidence while API returns `metadata.confidence`. [quiz/page.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/app/quiz/page.tsx) generates and locally grades demo questions. [quest-map.tsx](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/frontend/pages/quest-map.tsx) uses static data and component-memory progress only. |
| API | [backend/app/main.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/main.py): FastAPI 0.112.0, Pydantic 2.8.2; health, identity/protected/greeting, RAG, quiz routes. Uvicorn entry: `backend.app.main:app` from repository root. No upload/course/quest HTTP endpoints. |
| RAG logic | [rag.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/rag.py): signature-tolerant search, low-score guardrail, prompt, normalized citations, confidence. Separate kNN/retrieve/generate helpers exist but are not wired into the API. |
| Auth | [auth.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/auth.py) implements token-aware mock identity and role dependencies; real Cognito returns 501. **Disconnected:** main.py uses its own call-order role cycle/counters instead. Any nonempty Authorization header is accepted; roles are not token-derived. |
| Course data | [db.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/db.py): process-local class dictionary, keys `<course_id>#course` and `<course_id>#syllabus`, arbitrary payload dictionaries. DynamoDB mode creates a client but writes are no-ops and reads return None. Store is not connected to HTTP routes. |
| Quests | [quests.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/quests.py): syllabus `weeks[{week, topics}]` becomes deterministic read/quiz/apply quest dictionaries; disconnected from routes and the static quest screen. |
| Hosting/infra | [Compose](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/docker-compose.dev.yml) and [CI Compose](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/docker-compose.ci.yml) define backend, frontend, OpenSearch 2.9.0, LocalStack S3/DynamoDB. [Terraform](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/infra/terraform/main.tf) scaffolds S3, DynamoDB users/courses/study-events, and an OpenSearch Serverless **SEARCH** collection; no complete application hosting, Cognito, vector/security policies, or remote-state configuration. |

### RAG trace: what is implemented and what is missing

1. **Document upload/parsing:** no active S3 upload handler, PDF parser, Textract integration, or CLI entry point in [ingest.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/ingest.py). The documented `python -m app.ingest FILE --course ...` simply loads definitions and performs no ingestion. `pypdf` is not declared as a dependency.
2. **Chunking:** `chunk_pages` accepts already-extracted page strings and adds course/page/section metadata. `semantic_chunk_text` uses character windows despite token parameter names; it is not semantic/token-aware. Overlap greater than or equal to window size can prevent progress; do not probe that case without a timeout. `chunk_pages` does not split an oversized single line.
3. **Embeddings:** `StubEmbeddings` hashes text into deterministic vectors (default 16 dimensions), useful for repeatability rather than semantic similarity. No active real embedding provider.
4. **Storage/indexing:** `create_opensearch_index` attempts index creation, swallows all errors, and returns a mapping even on failure. Mapping contains both `vector.dims` and `embedding.dimension` and defaults to 1536 dimensions; real OpenSearch compatibility is unverified. No active bulk document indexing or ingestion orchestration.
5. **Retrieval:** the HTTP endpoint defines `_FakeSearch` inline and always returns Context A/B/C. It does not embed queries or read OpenSearch; `OS_HOST` is not consumed there. `course_id` is echoed in metadata and does not filter retrieval. The core's OpenSearch fallback uses a text match on `_all`, not its separate kNN helper. `rerank=True` is passed to clients but no internal reranker is implemented.
6. **Generation:** the endpoint defines `_FakeLLM` inline and returns a fixed stub response. [llm/adapter.py](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/app/llm/adapter.py) supplies StubLLM and an unimplemented Bedrock adapter, but the endpoint never calls its factory. OpenAI is not an application provider despite documentation references.
7. **Grounding:** low-scoring nonempty results trigger `NEED_MORE_SOURCES`; empty results or search failures instead substitute fake documents and can yield an apparently confident answer. This must change before treating answers as grounded. Citation dictionaries contain title/page/snippet/score, without actual source-document links; the endpoint caps them at three. Prompt context is not consistently capped by top_k.

**Feature status:** helper-level chunking, deterministic embeddings/LLM, in-memory course storage, quest transformation, validation, and quiz demo generation work within their limited contracts. Q&A screens, retrieval orchestration, mock auth, and quiz submission are partial/disconnected. Real ingestion/retrieval/generation, durable analytics, secure Cognito/RBAC, real quiz generation, uploads, personalized plans, collaboration, quotas, and production operations remain unfinished or planned. Quiz submission trusts client-supplied `correct` flags and persists nothing; UI sends `user_id: null` where API requires a string.

## Verification performed

All dependency installs and application/test runs used a disposable `git archive HEAD` copy at `/tmp/ragedu-restart.hoWvdZ`. Tests contain log-directory deletion hooks, and Next can auto-edit dependency/TypeScript files; isolation preserved the workspace. No paid APIs, shared-data writes, deployment, Terraform apply/plan, or external automation workflows were invoked. Servers were stopped afterward.

Environment: macOS; default Python 3.14.7, available Anaconda Python 3.13.5 used for an isolated venv; Node 24.12.0/npm 11.6.2. Documented baseline is Python 3.11/Node 20, **not verified here**. Docker daemon responds (29.7.2), no running containers were listed. Full container builds/services were not started.

| Check | Exact outcome |
| --- | --- |
| Backend requirements | Both production and development requirements installed successfully into isolated Python 3.13 venv. Resolved pytest 9.2.0/httpx 0.28.1; production pins retained. |
| Documented backend test shape | From backend/, `python -m pytest -q -p no:cacheprovider` fails collection: 7 errors because tests mix `app.*` and `backend.app.*` imports. |
| Backend with both paths | With root and backend on PYTHONPATH: **30 passed, 3 failed**. Failures: `test_main::test_rag_answer_success`, `test_main::test_rag_answer_defaults_when_omitted`, `test_rag_answer::test_success_creates_structured_log_and_returns_answer`. All encounter read-only `/app` when creating `/app/logs`. |
| Diagnostic only | In-memory reassignment of both imported main modules' `LOG_PATH` to working-directory `logs/app.json`: **33 passed**. No source changes. This demonstrates the immediate failure cause, not product correctness. |
| Live backend | Uvicorn starts on 127.0.0.1:18000. `/health` 200 `{"status":"ok"}`; valid `/rag/answer` 500 due to log mkdir; quiz generation 200; UI-shaped quiz submission 422 (`user_id: null`). Same invalid auth header twice yields student then professor, both 200. |
| Browser/API integration | CORS preflight to `/rag/answer` returns 405 without allow-origin. No CORS middleware or frontend API rewrites exist. Default empty API URL routes requests to Next instead of FastAPI; a direct backend URL requires CORS or a proxy. |
| Frontend install/build | `npm ci` fails because frontend has no lockfile. Disposable-copy `npm install --no-package-lock --no-audit --no-fund` succeeds. `npm run build` fails on conflicting `pages/index.js` and `app/page.tsx`. |
| Frontend startup | Dev startup attempts auto-installing undeclared TypeScript/@types dependencies through yarn, then fails in Next's TypeScript setup with `Cannot read properties of undefined (reading 'endsWith')`. Auto-resolved TS 7.0.2/types React 19 under Node 24 are not a validated baseline. No working browser journey established. |
| Frontend tests | No test/lint scripts or configured runner. `__tests__/Demo.test.tsx` exists but was not executed. |
| Other local checks | `bash -n backend/scripts/e2e_smoke.sh` passes; Compose CI `config --quiet` passes; `mkdocs build --strict --site-dir /tmp/ragedu-restart.hoWvdZ/site` passes, including the completed briefing. No live AWS/OpenSearch/PDF/LLM or Terraform validation. |

### Reproduce safely

Use an isolated checkout/archive, especially for tests; do not run test cleanup hooks against valuable `logs/` directories. Example from repository root (replace Python executable with a supported installed version):

```sh
RESTART_TMP=$(mktemp -d /tmp/ragedu-check.XXXXXX)
git archive HEAD | tar -x -C "$RESTART_TMP"
cd "$RESTART_TMP"
python3 -m venv venv
venv/bin/pip install -r backend/requirements.txt -r backend/requirements-dev.txt
export PYTHONPATH="$RESTART_TMP:$RESTART_TMP/backend"
cd backend
../venv/bin/python -m pytest -q -p no:cacheprovider
cd ..
venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 18000
# In another terminal, probe http://127.0.0.1:18000/health and POST /rag/answer.
# Stop server with Ctrl+C.
cd frontend
npm ci # expected failure: missing frontend lockfile
npm install --no-package-lock --no-audit --no-fund
NEXT_TELEMETRY_DISABLED=1 npm run build # expected root-route conflict
```

No environment secrets are necessary for today's inline fake API. All inspected relevant variables were unset in this session: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_BACKEND_URL`, `BACKEND_LLM_PROVIDER`, `COGNITO_USER_POOL_ID`, `AWS_REGION`, `AWS_DEFAULT_REGION`, `AWS_ENDPOINT_URL`, `AWS_ENDPOINT_URL_S3`, `USE_IN_MEMORY_DB`, `BEDROCK_MODEL_ID`, `OPENAI_API_KEY`, `OS_HOST`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`. No secret values were read or recorded. `frontend/.env.example` correctly names `NEXT_PUBLIC_API_URL`; setup docs incorrectly use `NEXT_PUBLIC_BACKEND_URL`. Provider/auth/DB variables affect disconnected helpers, not the inline API behavior; supplying credentials will not complete integrations.

### CI/deployment caveats

[preview-test.yml](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/.github/workflows/preview-test.yml) waits for a health body containing `"ok"`; the real server returns `{"status":"ok"}`. `/health` changes shape using `PYTEST_CURRENT_TEST`, masking inconsistent contracts. The backend image healthcheck uses curl, which its slim Dockerfile does not install. [e2e_smoke.sh](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/backend/scripts/e2e_smoke.sh) passes shell syntax checking but has conflicting heredoc/stdin handling, expects `ok: true`, and sends unsupported `q` instead of `query`/`question`. [ephemeral-check.yml](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/.github/workflows/ephemeral-check.yml) also uses frontend `npm ci` without a lockfile. These are source-derived blockers; CI was not triggered and remote run status is unknown. [docs.yml](https://github.com/ksdbh/RAGEdu-starter/blob/8093421d152233cfe9117594877cf6913a48af0b/.github/workflows/docs.yml) deploys MkDocs to GitHub Pages; no verified application deployment exists. Makefile infra helpers target `infra/`, but actual Terraform root is `infra/terraform/`. Scheduled log-triage/assistant workflows can call OpenAI/create issues; none were invoked.

## Recommended restart milestone and top three tasks

**Milestone: a reproducible local course Q&A slice, starting with an explicitly labeled demo and ending with one ingested document.** Keep quizzes, quest persistence, cloud rollout, and broad refactoring outside this milestone.

1. **Restore the local Q&A demo and honest verification baseline (recommended first task).** Resolve duplicate root ownership (recommend App Router Q&A as home; retain/move auth demo deliberately), declare compatible TypeScript/test dependencies and frontend lockfile, normalize backend import/test invocation and writable logging, choose one health schema, and connect browser/API through one documented URL/proxy strategy. Replace call-order auth with the existing token-aware mock dependency and adjust tests to assert repeatable behavior. Align smoke/CI contracts with actual routes. This removes immediate development friction and prevents green tests from masking invalid identity behavior.
2. **Connect one document end to end without external model costs.** Review historical ingestion/retrieval implementations; implement a real local PDF CLI, page/source metadata, compatible index mapping and vector dimensions, bulk storage, query embedding/retrieval, course filtering, and injected provider clients. Start with deterministic offline generation and clearly label its limitations; choose retrieval/embedding approach explicitly rather than pretending hash vectors are semantic embeddings. Empty/error retrieval must return insufficient evidence, never demo sources. Add a fixture-based ingestion→answer contract test with real source citations and cross-course isolation.
3. **Validate educational answer quality with the chosen real provider.** After a product/provider decision and separately authorized API usage, add one generation/embedding integration, a small course question evaluation set, grounded citation checks, and answerable/unanswerable cases. Define acceptable quality before expanding quizzes or deployment. Keep no-cost offline tests as the default.

### First-task acceptance criteria

- A fresh environment on documented Python/Node versions installs reproducibly, with frontend lockfile and required TS dependencies committed; no startup auto-install or prompts.
- One `/` route builds and serves. A user can open home, ask a question, and see a clearly labeled demo answer and readable page/snippet citations; empty input and backend errors render useful messages.
- Browser request reaches FastAPI without CORS/proxy errors using one documented variable/configuration. No keys or AWS services required.
- Valid RAG requests work on macOS/Linux without needing `/app`; logs use a configurable/writable destination. Logging failure does not take down Q&A.
- One documented backend test command collects all tests; tests assert one runtime health schema without caller detection. Repeated and reordered token requests return stable roles; invalid tokens return 401 and student access to professor route consistently returns 403.
- Offline backend suite, frontend production build, a minimal browser Q&A check, and the corrected smoke script pass. CI health/install steps use those same contracts. This task need not claim real retrieval or secure production auth.

## Product decisions still needed

These do not block the first local-reliability task:

- Is **RAGEdu** or **EduRAG** the intended public name?
- Is the next demonstration chiefly course Q&A, or was the syllabus/quest learning workflow the intended primary product? Repository evidence favors Q&A but does not establish a product decision.
- Which representative course/PDF and student questions should define the first meaningful end-to-end acceptance set? Are materials licensed/appropriate to process locally and with an eventual external model?
- For the next connected slice, must AWS/OpenSearch/Bedrock be retained, or is a simpler offline development store acceptable? Which provider/budget should eventually govern embeddings and generation?

Future sessions should start here, compare HEAD/worktree with the baseline above, and update verified results as implementation progresses.
