# Changelog and current development handoff

## 2026-10-30 — persistent PDF search and cited course excerpts

Baseline: `7c7785a545f22f70ecefad78c9a158d67a8c1be2`. This pass delivers four focused tasks. The October 28 section below is historical; its dependency and ingestion blockers are superseded by this entry.

| Task | Commit | Delivered behavior |
| --- | --- | --- |
| 1. Resolve dependency advisories | `afb482f` | Next 16.4.3, React 19.3.1, Vitest 5.0.5 and matching types; Node 24 tooling/CI/container baseline, fresh route type generation, lockfile and migration verification. |
| 2. Implement local PDF ingestion | `3a10a05` | Real pypdf parser/CLI, page-preserving bounded chunks, persistent course-scoped SQLite FTS5 index, atomic idempotent re-imports, clear failure cases and regression tests. |
| 3. Connect cited course search | `4d95986` | Explicit local/demo services, course/status API, required local course scope, actual source identifiers/page citations, shared home/demo UI, DOM integration tests and both-mode HTTP/proxy CI smoke. Adds the synthetic example PDF; DOM tooling requires Node 24.15+ (or supported Node 26+). |
| 4. Record verified handoff | This documentation commit | Updated README, local-course-search guide, setup/API/testing notes and restart-brief status; preserves historical evidence and defines the next milestone. |

### What works now

A text PDF can be imported with one CLI command; a fresh API process reads its persisted passages; home and `/demo` select the course and quote actual matching sources with page numbers. Identical-byte imports into the same course replace passages without duplicates. Another course cannot contribute passages to the selected course's response. Empty/failed retrieval never substitutes sample sources.

This is **keyword retrieval plus verbatim source excerpts**. Semantic embeddings and LLM synthesis remain unimplemented in this path. Default mode remains explicitly simulated; enable local mode deliberately. Core code: `ingest.py`, `local_index.py`, `study.py`, `main.py`, `rag.py`, and `frontend/components/Study.tsx`.

### Verification on October 30

- **64 backend tests pass**, including real PDF extraction, original page numbers after blank pages, a fresh-process read, idempotence/rollback, cross-course filtering, invalid/scanned/encrypted inputs, bounded requests, runtime faults, and newly ingested material becoming visible without an API restart.
- **8 frontend DOM component tests pass**, covering course payloads/citations, clearing old evidence on course changes, empty/failed states, disabled unconfigured search, and the demo path. These replace the former three confidence-label utility tests.
- Clean `npm ci`, route type generation/TypeScript, production build, and **full `npm audit` (production and development): zero vulnerabilities**. Verified with isolated Node **24.22.2**; Python **3.13.5**, SQLite **3.45.3**. CI targets Python 3.11/current Node 24.
- Real CLI ingests `backend/examples/graphs.pdf` into a temporary SQLite corpus. Live API and production Next servers pass smoke checks in both demo and local modes, directly and through the same-origin proxy. Local Dijkstra response cites `graphs.pdf`, page 1; unrelated/wrong-course queries return no citations. All five UI routes return HTTP 200.
- Both Compose configurations validate; all workflow YAML parses; smoke shell syntax and strict MkDocs build pass. Full container startup and an interactive real-browser session were not exercised. DOM tests do not verify browser hydration or visual layout. One existing upstream Starlette/AnyIO warning remains.
- The prior October 28 [Preview tests](https://github.com/ksdbh/RAGEdu-starter/actions/runs/40757085908) and [Docs](https://github.com/ksdbh/RAGEdu-starter/actions/runs/40757085847) runs are now confirmed successful. The new implementation [Preview tests run](https://github.com/ksdbh/RAGEdu-starter/actions/runs/41067715620) at `4d95986` **passed**, including Python 3.11 backend checks, Node 24 frontend build/checks, and demo/local API-plus-proxy smoke. Consult GitHub for final status of the documentation commit too.
- No AWS/model calls, paid APIs, infrastructure mutation, or application deployment. Local verification used a temporary index; the existing stash was preserved. Pushes trigger normal repository CI/docs workflows.

### Resume commands and configuration

Use the updated root README, or the [local search guide](guides/local-course-search.md). From root/activated venv:

```sh
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m backend.app.ingest backend/examples/graphs.pdf --course CS101
RAGEDU_MODE=local python -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal, `cd frontend && npm ci && npm run dev`. Open home, choose CS101, ask “What does Dijkstra require?” `data/courses.sqlite3` is ignored by Git. Use CLI `--index` and API `RAGEDU_INDEX_PATH` together when changing paths. The default API mode is `demo`. `BACKEND_URL` remains server-only Next proxy configuration; `RAGEDU_LOG_PATH` remains optional logging configuration.

For the supplied sample, root `EXPECTED_MODE=local COURSE_ID=CS101 bash backend/scripts/e2e_smoke.sh`; repeat with `BASE_URL=http://localhost:3000/api/backend` to exercise the proxy. The smoke query expects two sample passages. For tests: root `python -m pytest -q`; frontend `npm test`, `npm run typecheck`, `npm run build`, `npm audit`.

### Where we left off / next milestone

**Next: evaluate retrieval against representative course questions before choosing semantic search or a generation provider.** The fixture proves connectivity and isolation; it does not establish educational answer quality. Select a real permitted PDF, record expected relevant pages for answerable questions and no-source cases, and measure keyword retrieval misses. Agree on whether excerpt search is sufficient or the product needs synthesized explanations.

Concrete acceptance criteria: a checked-in, non-sensitive evaluation set or reproducible local evaluation format; expected page/source IDs for answerable cases; no cross-course matches; empty/failed index and no-match cases produce no answer citations; reported retrieval coverage/limitations. If paraphrase recall is inadequate, choose one real semantic embedding/storage approach. If explanations are required, choose provider/budget and validate grounded answers with the same sources; keep offline tests as the default.

Remaining boundaries: trusted text PDFs only, no OCR/upload service, no document-serving endpoint, no index deletion/version-management UI, simple character chunking/English stopwords, no course authorization, no persistent quiz/quest progress. Changed PDF bytes become a new document rather than replacing old versions. Course selection is filtering, not access control. AWS/OpenSearch/provider requirements and final RAGEdu/EduRAG naming still need product decisions.

## 2026-10-28 — restart pass: local demo restored

Inspection baseline: `8093421d152233cfe9117594877cf6913a48af0b`. Seven implementation/investigation commits are listed below; the eighth commit is this documentation handoff. Public naming remains undecided (RAGEdu/EduRAG).

### Eight completed tasks / commits

| Task | Commit | Result |
| --- | --- | --- |
| 1. Recover repository context | `eca6fab` | Saved dated restart briefing, architecture evidence, stash/branch findings, historical recovery candidates, and milestone. |
| 2. Repair local backend verification | `58e14b1` | Root pytest configuration, canonical imports, portable configurable request logs, temporary test logs; log failures no longer fail requests. |
| 3. Restore deterministic identity/health | `d63e3c2` | Existing token-aware mock auth is wired into routes; repeated/reordered requests and invalid tokens are tested. One runtime health schema replaces test-name detection. |
| 4. Make retrieval fail honestly | `003d2f3` | Empty/error/unusable evidence refuses generation instead of inventing sources; real search-client shapes and matching top-k context/citation limits are tested. API marks demo mode. |
| 5. Repair frontend setup/routing | `1766d79` | Auth screen moved to `/auth`; lockfile, TypeScript dependencies, and runnable Vitest tests added. Next updated within 14.x to 14.2.35. |
| 6. Connect demo screens | `66162a0` | Same-origin backend proxy shared by Q&A/demo/auth/quiz; readable citations and explicit demo labels; quiz submission uses valid demo identity. Compose receives backend address and a Python health probe. |
| 7. Repair local smoke/CI | `bb396e6` | Smoke checks validate health, sample sources, and explicit demo mode without response files. CI runs backend/frontend checks and API/proxy smoke without AWS or model calls; container entry point normalized. |
| 8. Publish resumable handoff | `7c7785a` | README quickstart, this changelog, restart-brief update, and core setup/testing guidance reflect verified current behavior and the next milestone. |

### Verified current state

- **45 backend tests pass**, including invalid/reordered auth, evidence guardrails, and unwritable-log regression cases. One upstream Starlette/AnyIO deprecation warning remains.
- **3 frontend tests pass**; TypeScript check and production build pass. `npm ci` succeeds with the committed frontend lockfile.
- Live Uvicorn and Next production servers start. The smoke script passes against FastAPI on port 18000 and through Next's `/api/backend` proxy on port 13000. All five UI routes respond HTTP 200; home HTML contains the question label and demo disclosure.
- Both Compose files validate; workflow YAML parses; smoke shell syntax and strict MkDocs build pass. Actual GitHub Actions runs and full Docker stack startup were not verified locally.
- Local checks used macOS, Python 3.13.5 (isolated venv), Node 24.12.0/npm 11.6.2. CI specifies Python 3.11/Node 20.19.0. No available browser session: interactive clicks, visual layout, and browser hydration were not verified.
- Production audit (`npm audit --omit=dev`) reports **2 dependency entries: Next critical, PostCSS high**. The 14.x patch applied per the [December 2025 Next.js guidance](https://nextjs.org/blog/security-update-2025-12-11) does not address all later advisories. This is a local-demo milestone, not production readiness; plan a supported-release migration before public hosting.
- No AWS/model calls, infrastructure changes, paid APIs, or application deployments were performed. Existing stash was preserved. Push/CI status should be checked on GitHub after publication; local verification does not establish remote workflow success.

### Reproduce

Use the root README quickstart. From an activated backend environment, root `python -m pytest -q`; from `frontend/`, `npm ci`, `npm test`, `npm run typecheck`, `npm run build`. Start backend on 8000 and frontend on 3000. From root run `bash backend/scripts/e2e_smoke.sh`, then `BASE_URL=http://localhost:3000/api/backend bash backend/scripts/e2e_smoke.sh`.

`BACKEND_URL` is server-only Next configuration, default `http://127.0.0.1:8000`. Restart/rebuild after changing it. Compose uses `http://backend:8000`. `RAGEDU_LOG_PATH` optionally overrides `logs/app.json`. Demo operation requires no credentials. It is deliberately simulated even if cloud environment variables are supplied.

### What remains / next tasks

1. **Before public deployment: address dependency advisories.** Select a supported Next.js version, inspect migration requirements, update React/tooling as required, rerun audit/build/tests and browser smoke. Do not use a forced audit fix without reviewing migration behavior. This can remain separate from offline ingestion development.
2. **Core product milestone: connect one actual PDF to Q&A.** Review historical `815a2fb` ingestion and `7d18f45` retrieval implementations and the restart briefing. Implement local parsing, stable document/page/course identifiers, compatible storage/vector dimensions, query retrieval with course isolation, and dependency-injected search/generation. Keep external generation optional and offline tests default. Empty evidence must remain insufficient evidence.
3. **Evaluate on representative course questions.** Pick a course/PDF and answerable/unanswerable questions; choose model/provider/budget before external calls. Validate citation fidelity and response usefulness, then consider quizzes, syllabus quests, durable progress, and secure production auth.

Acceptance for the next core slice: a fixture PDF can be ingested with one documented command; a new process retrieves its actual passages; home Q&A returns document/page citations from that corpus; another course's content cannot leak; empty or failed retrieval never emits demo sources; offline integration checks exercise the full path. Hash vectors must not be described as semantic embeddings. Backend/API demo clients remain explicit until this slice is delivered.

Product decisions still needed: final name, Q&A versus quest workflow priority, representative materials/permissions, and whether AWS/OpenSearch is mandatory for the next slice. These decisions do not undo the completed local-demo fixes.

## 0.1.0 — initial scaffold

Initial scaffold and documentation added. See [restart investigation](RESTART_BRIEF.md) for reconstructed historical context.
