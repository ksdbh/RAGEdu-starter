# EduRAG — AI study companion grounded in your course content

[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/preview-test.yml/badge.svg?branch=main)](https://github.com/<OWNER>/<REPO>/actions/workflows/preview-test.yml)
[![Docs](https://ksdbh.github.io/RAGEdu-starter/)](https://ksdbh.github.io/RAGEdu-starter/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Tagline: EduRAG — a Retrieval-Augmented Generation scaffold that answers student questions with citations from course materials.

---

## Pitch — why EduRAG

Students and instructors need fast, reliable answers tied to course materials (slides, PDFs, syllabi). LLMs are powerful but can hallucinate or lose context. EduRAG provides a scaffolded RAG pipeline that keeps responses grounded in course content by combining document ingestion, semantic chunking, embeddings, vector search, and LLM synthesis with citations.

How it works (high level):

- Ingestion: upload PDFs / slides to S3 (or run local ingest CLI) — files are OCR'd or parsed.
- Chunking: documents are split into semantic chunks with light metadata (page, section, course).
- Embedding: text chunks are converted to vector embeddings (Bedrock / OpenAI or local stub).
- Indexing / Retrieval: vectors are stored in OpenSearch (or a stub) for fast similarity search.
- Answer generation: FastAPI composes top-k retrieved passages into a prompt for an LLM (Bedrock / OpenAI) and returns answers with citations to the frontend.

---

## Architecture (data flow)

```mermaid
flowchart LR
  S3[S3 (uploaded PDFs / documents)] --> Textract[Amazon Textract / PDF parser]
  Textract --> Chunking[Semantic chunking & metadata]
  Chunking --> Embedding[Embedding service (Bedrock / OpenAI / stub)]
  Embedding --> OpenSearch[OpenSearch (vector index) / stub]
  OpenSearch --> FastAPI[FastAPI (backend/app/main.py)]
  FastAPI --> LLM[LLM (Bedrock / OpenAI / stub)]
  LLM --> FastAPI
  FastAPI --> NextJS[Next.js frontend (frontend/)]

  classDef aws fill:#f3f4f6,stroke:#111827
  class S3,Textract aws
```

---

## Getting started (local developer onboarding)

This README is intended to be the front door for developers. Replace placeholders below (OWNER, REPO, BRANCH, and docs_url) with your repository-specific values.

Prerequisites

- Git
- Python 3.11
- Node 20 / npm
- Docker (optional for devcontainer and docker-compose)
- Make (optional; convenience targets included)
- (Optional) Terraform & AWS CLI when working with infra

Clone the repository

```bash
git clone https://github.com/<OWNER>/<REPO>.git
cd <REPO>
# or use your fork / org URL
```

Devcontainer

This repo includes an opinionated VS Code devcontainer (.devcontainer/devcontainer.json). Opening in the container will run the post-create steps:

- pip install -r backend/requirements.txt
- cd frontend && npm i

Local backend (FastAPI)

- Backend entrypoint: backend/app/main.py

Start the backend with hot reload:

```bash
# from repo root
# option A: Use Makefile helper
make backend-run

# option B: direct uvicorn (explicit path)
cd backend
uvicorn backend.app.main:app --reload --port 8000
```

Notes / environment variables (local dev)

- BACKEND_LLM_PROVIDER=stub        # use the local LLM stub
- OPENAI_API_KEY                   # when calling OpenAI paths
- COGNITO_USER_POOL_ID, AWS_REGION # for real Cognito (optional)
- AWS_ENDPOINT_URL                 # local endpoints (LocalStack) if used

Local frontend (Next.js)

- Frontend entrypoint: frontend/ (Next.js app)

```bash
cd frontend
npm ci
# Point the frontend to the backend as needed
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

Docker / CI-style local run

To run the services using the CI compose file (useful for integration testing):

```bash
# builds images and brings up services using the CI compose file
docker compose -f docker-compose.ci.yml up --build
```

Makefile conveniences

Available targets (see Makefile):

- make devcontainer-setup   - install backend & frontend deps
- make backend-run          - run the FastAPI app (uvicorn)
- make backend-test         - run pytest in backend/
- make ingest FILE=...      - run ingestion CLI (from backend/)
- make frontend-install     - cd frontend && npm ci
- make frontend-dev         - cd frontend && npm run dev
- make infra-plan/apply/destroy - terraform helpers (if infra/ exists)

---

## Testing

Backend unit tests

```bash
# recommended: from repo root
make backend-test
# or
cd backend
pytest -q
```

Frontend tests

```bash
cd frontend
# if tests are present
npm test
```

CI/CD

- GitHub Actions workflows run on PRs and pushes. Example workflows:
  - .github/workflows/preview-test.yml — runs backend tests, builds frontend, uploads artifacts.
  - .github/workflows/preview-aws.yml — optional: provisions preview infra (Terraform) for PRs.

Workflows are configured to publish badges in this README — update the OWNER/REPO/BRANCH placeholders above to have valid badge links.

---

## Reference — quick links

- Developer docs portal: {{ docs_url }}
- Backend entrypoint: backend/app/main.py
- Ingest CLI: backend/app/ingest.py
- Auth helpers (mock + Cognito): backend/app/auth.py
- DB fallback store: backend/app/db.py
- Frontend: frontend/ (Next.js)
- RAG pipeline overview (docs): {{ docs_url }}/rag.md
- Operations / Runbooks: {{ docs_url }}/runbooks.md
- Testing docs: {{ docs_url }}/testing.md
- CONTRIBUTING guide: ./CONTRIBUTING.md
- Changelog: {{ docs_url }}/changelog.md

Note: replace {{ docs_url }} with your MkDocs Material site URL (or local docs path if serving docs with mkdocs serve).

---

## Roadmap

- ✅ Implemented: MVP scaffold — ingestion CLI, chunking & embedding stubs, FastAPI RAG skeleton, minimal Next.js UI, mock auth.

Short / Medium term (🔜):

- Improve RAG prompts and citation formatting
- Add role-based Cognito integration and RBAC
- Add quizzes & practice tests with analytics (DynamoDB)
- Improve ingestion granularity (slide-level metadata)

Long term (📈):

- Fine-grained observability, quotas & cost controls for LLM usage
- Automated syllabus mapping and personalized study plans
- Collaborative features: shared flashcards, study groups

Full changelog & roadmap: {{ docs_url }}/changelog.md

---

## Contributing

We welcome contributions. Quick guidance:

- Small PRs are preferred: 1 feature/fix per PR with tests and changelog note.
- For large design changes, open an Issue first to align on architecture and scope.
- If you touch infra, include terraform plan output and mark PRs with the infra label.

See ./CONTRIBUTING.md for the full contributor workflow and local dev tips.

PR checklist (suggested):

- [ ] Ran `mkdocs serve` locally to confirm docs references
- [ ] Verified workflow badges resolve (update OWNER/REPO placeholders)
- [ ] Verified paths referenced in README exist (backend/, frontend/, infra/)
- [ ] Ran `markdownlint README.md` (or your preferred markdown linter)

---

## License

This repository is distributed under the MIT License. Replace or update the LICENSE file if your project uses a different license.

---

## Where to go next

For more, see the full Developer Docs » {{ docs_url }}

If you hit problems while setting up, open an Issue with the OS, error logs, and the step that failed — maintainers will help. Thank you for contributing to EduRAG.
