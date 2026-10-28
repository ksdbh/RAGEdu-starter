# Changelog and current development handoff

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
| 8. Publish resumable handoff | This documentation commit | README quickstart, this changelog, restart-brief update, and core setup/testing guidance reflect verified current behavior and the next milestone. |

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
