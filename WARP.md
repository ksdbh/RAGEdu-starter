# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository overview

EduRAG (RAGEdu-starter) is a scaffolded Retrieval-Augmented Generation (RAG) study assistant. It ingests course materials (PDFs/slides), chunks and embeds them, stores vectors in OpenSearch (or a stub), and exposes a FastAPI backend plus a minimal Next.js frontend.

Top-level layout (see `docs/project-structure.md` for more detail):
- `backend/` – FastAPI app, ingest/embedding utilities, RAG core, auth/db helpers, tests.
- `frontend/` – Next.js 14 app used as the web UI.
- `infra/` – Terraform scaffolding (S3, DynamoDB, OpenSearch, etc.).
- `docs/` – MkDocs Material docs; treat this as the canonical developer documentation.

The published docs site (from `README.md`) is the best entry point for deeper background: `https://ksdbh.github.io/RAGEdu-starter/`.

## Common commands

Prefer using the `Makefile` helpers from the repo root when possible; they mirror the steps documented in `README.md`, `CONTRIBUTING.md`, and `docs/getting-started.md`.

### Backend (FastAPI)

From repo root unless noted otherwise:

- Install dependencies (no venv management):
  - `pip install -r backend/requirements.txt`
- Install dependencies with a project venv (Makefile convenience):
  - `make backend-install`
- Run the API with hot reload on `http://localhost:8000`:
  - `make backend-run`
  - or `uvicorn backend.app.main:app --reload --port 8000`
- Run all backend tests:
  - `make backend-test`
  - or `cd backend && pytest -q`
- Run a single backend test (pytest pattern):
  - `cd backend && pytest backend/tests/test_rag_answer.py::test_rag_answer_happy_path`
  - Adjust the file and test name as needed; all tests live under `backend/tests/`.
- Run the ingestion CLI:
  - `make ingest FILE=path/to/file.pdf COURSE=CS101`
  - or `cd backend && python -m app.ingest path/to/file.pdf --course CS101`

Key environment variables used by the backend (see `README.md`, `docs/getting-started.md`, and backend code):
- `BACKEND_LLM_PROVIDER` – selects LLM provider; defaults to `stub` (see `backend/app/llm/adapter.py`).
- `OPENAI_API_KEY` – required for any real OpenAI-backed paths.
- `COGNITO_USER_POOL_ID`, `AWS_REGION` – presence of a pool ID switches `auth` to the real Cognito client; otherwise the mock client is used.
- `AWS_ENDPOINT_URL` / `AWS_ENDPOINT_URL_S3` – local endpoints (e.g., LocalStack) for DynamoDB/S3 if configured.

### Frontend (Next.js)

From repo root unless noted otherwise:

- Install dependencies:
  - `make frontend-install`
  - or `cd frontend && npm ci`
- Run the dev server (Next.js, default port 3000):
  - `make frontend-dev`
  - or `cd frontend && npm run dev`
- Build the frontend for production:
  - `make frontend-build`
  - or `cd frontend && npm run build`
- Start the production server after a build:
  - `cd frontend && npm run start`
- Point the frontend at a local backend (from `docs/getting-started.md`):
  - `export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`

The scaffold does not currently define an `npm test` script in `frontend/package.json`; follow your preferred Next.js testing setup if you add one.

### Docker Compose (backend + frontend + infra stubs)

For a composed local environment with backend, frontend, OpenSearch, and LocalStack:

- CI-style stack (mirrors GitHub Actions):
  - `docker compose -f docker-compose.ci.yml up --build`
- Dev stack (same services, convenient for local experimentation):
  - `docker compose -f docker-compose.dev.yml up --build`

Both Compose files build from the local `backend/` and `frontend/` Dockerfiles and wire OpenSearch and LocalStack for vector search and AWS stub services.

### Terraform / infrastructure

Infra commands can be run directly in `infra/terraform` or via the Makefile helpers:

- Direct Terraform (from `infra/terraform`, see its `README.md`):
  - `terraform init`
  - `terraform plan -var="project=myproj" -var="region=us-east-1"`
  - `terraform apply -var="project=myproj" -var="region=us-east-1"`
- Makefile shortcuts (from repo root, operate if `infra/` exists):
  - `make infra-plan`
  - `make infra-apply`
  - `make infra-destroy`

The Terraform in this repo is intentionally minimal scaffolding; state backends and production hardening are left to the consumer (see `infra/terraform/README.md`).

### Linting and formatting

Lint/format commands are best-effort and depend on tools being installed or scripts being defined:

- Aggregate lint (from `Makefile`):
  - `make lint` – runs `flake8` on `backend/` if available, and `npm run lint` in `frontend/` if configured.
- Aggregate format:
  - `make format` – runs `black` on `backend/` if available, and `npm run format` in `frontend/` if configured.

If you add stricter linters/formatters or frontend lint/format scripts, update the `Makefile` accordingly.

## High-level architecture

Use `docs/architecture.md` and `docs/project-structure.md` as the authoritative references; the summary below is to orient future agents quickly.

### Data and request flow

End-to-end flow (from `README.md` and `docs/architecture.md`):
- **Ingestion**: PDFs/slides are uploaded (e.g., to S3 or via a local CLI) → text is extracted → content is chunked into passages with metadata → chunks are embedded into vectors → vectors plus metadata are stored in OpenSearch (or a stub).
- **Query time**: The frontend calls the FastAPI backend → backend retrieves similar chunks from the vector store → a configured LLM synthesizes an answer grounded in those chunks and returns citations.

### Backend layout (`backend/app/`)

Key modules and their roles:
- `main.py`
  - Defines the FastAPI app and HTTP routes.
  - Health endpoint (`/health`) has deterministic behavior tailored to the test suite.
  - Identity/protected routes (`/whoami`, `/protected/*`, `/greeting`) demonstrate auth flows and role-based behavior.
  - RAG endpoint (`POST /rag/answer`) validates query payloads, enforces `top_k` constraints, logs JSON lines to `/app/logs/app.json`, and delegates to `rag.answer_query` using simplified fake search/LLM clients.
  - Quiz endpoints (`/quiz/generate`, `/quiz/submit`) provide a minimal question generator and scoring path.

- `rag.py`
  - Contains the core RAG orchestration logic.
  - `answer_query(...)` is the central function: it is tolerant of multiple search client signatures, normalizes OpenSearch-style results, applies a similarity-based guardrail (`GUARDRAIL_NEED_MORE_SOURCES`) before any LLM call, and returns an answer with normalized citations and a confidence score.
  - Also contains lower-level helpers (`build_knn_query`, `retrieve`, `generate_answer`, `rag_answer`) for more traditional retrieve→generate flows.

- `ingest.py`
  - Implements text and page chunking primitives (`semantic_chunk_text`, `chunk_pages`) that operate on raw text or page strings and attach course/page/section metadata.
  - Provides `StubEmbeddings` for deterministic, local embedding vectors and `create_opensearch_index(...)` for building a simple vector-ready index mapping.

- `auth.py`
  - Defines an auth model (`User`) plus `CognitoClientInterface` and two implementations:
    - `MockCognitoClient` – default in local/CI; decodes simple tokens like `student_token`, `prof_token`, `admin_token`, and `mock:alice|professor`.
    - `RealCognitoClient` – skeleton that currently returns an HTTP 501 error if used without a concrete implementation.
  - `get_cognito_client()` selects the implementation based on `COGNITO_USER_POOL_ID`/`AWS_REGION`.
  - Exposes FastAPI dependencies such as `get_current_user`, `get_current_user_optional`, and `require_role(role)` for role-based access control.

- `db.py`
  - Provides `CourseSyllabusStore`, a simple course/syllabus store that defaults to an in-memory dictionary for CI and dev.
  - Can optionally back onto DynamoDB if AWS credentials and endpoints are configured; Dynamo behavior is deliberately stubbed for this scaffold.

- `llm/adapter.py`
  - Defines a minimal `LLMProvider` protocol and two implementations:
    - `StubLLM` – deterministic stub that echoes prompts, constructs citation markers from context blocks, and emits short context excerpts; used by default.
    - `BedrockLLM` – unimplemented skeleton meant to be wired to AWS Bedrock in real deployments.
  - `get_llm()` is the factory controlled by the `BACKEND_LLM_PROVIDER` environment variable.

Backend tests live under `backend/tests/` and cover auth, chunking, DB behavior, RAG guardrails, quiz endpoints, and the HTTP API. They use FastAPI's `TestClient` with the mock auth tokens described in `docs/getting-started.md` and `CONTRIBUTING.md`.

### Frontend layout (`frontend/`)

The frontend is a Next.js 14 application configured via `frontend/next.config.js` and `frontend/package.json`.

- Scripts:
  - `npm run dev` – dev server.
  - `npm run build` – production build.
  - `npm run start` – start built app.
- It is intended as a minimal UI over the backend RAG and auth flows, with the backend base URL provided via `NEXT_PUBLIC_BACKEND_URL`.
- For detailed structure (pages/components), inspect the `frontend/` directory directly; there are no additional framework-level constraints beyond standard Next.js conventions.

### Infrastructure (`infra/`)

Terraform under `infra/terraform` provisions a minimal set of AWS resources (see its `README.md`):
- S3 bucket for docs/content.
- DynamoDB tables for users, courses, and study events.
- OpenSearch Serverless collection for vector search.

The modules are intentionally minimal; remote state configuration and production security/scale settings are left to the consumer.

### Documentation (`docs/`)

The `docs/` tree is an MkDocs Material site that captures the intended architecture and workflows:
- `docs/index.md` – high-level developer guide and table of contents.
- `docs/getting-started.md` – prescriptive local setup for backend/frontend and mock auth tokens.
- `docs/architecture.md` – RAG architecture and runtime flow.
- `docs/project-structure.md` – summary of `backend/`, `frontend/`, `infra/`, and common commands.
- `docs/backend.md` – HTTP endpoint catalog for the backend.
- `docs/testing/*` – testing strategy, how to run tests, and test conventions.
- Additional subtrees for RAG design, operations, security, and AWS integrations.

When making non-trivial changes, prefer updating the relevant `docs/` pages in parallel so that the external docs site and this WARP guidance stay in sync.