# EduRAG — AI study companion grounded in your course content

Tagline: EduRAG — AI study companion grounded in your course content

🚀 High-level pitch

Students struggle to surface the right passages from slides, PDFs and syllabi when studying: notes get scattered, search returns noisy results, and context is lost when asking an LLM. EduRAG addresses these pain points by combining semantic retrieval over your course materials with an LLM that composes grounded answers with citations.

This scaffold demonstrates a Retrieval-Augmented Generation (RAG) approach on AWS: ingest PDFs → extract text (Textract) → chunk & embed → index vectors (OpenSearch) → retrieve + synthesize answers with an LLM (Bedrock / OpenAI). Our vision is a lightweight, secure, and extensible study assistant that helps students learn faster while keeping answers tied to course sources.

🧭 Quick architecture (visual)

```mermaid
flowchart LR
  %% --- Components ---
  S3[(S3: Uploaded PDFs & Docs)]
  Textract[[Textract / PDF Parser]]
  Chunker[Chunker + Metadata]
  Embed[Embeddings (Bedrock Titan)]
  OS[(OpenSearch Vector Index)]
  API[FastAPI RAG API]
  LLM[[Bedrock LLM<br/>(Claude / Titan)]]
  FE[Next.js Frontend]

  %% --- Ingestion path ---
  S3 --> Textract --> Chunker --> Embed --> OS

  %% --- Retrieval path ---
  FE <--> API
  API --> OS
  API --> LLM
  LLM --> API
  API --> FE
```

📚 Quick start — local development

Prereqs: Git, Python 3.11, Node 20, Docker (optional), Make (convenience targets available in the Makefile).

1. Clone the repo

   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo
   ```

2. Devcontainer (optional): The repo includes a .devcontainer that runs postCreateCommand to install backend + frontend deps.

3. Local (fast) startup using the stub LLM provider

   - The repo includes a docker-compose.ci.yml for simpler CI-style builds and local integration testing. To build/run the services with the CI compose file:

     ```bash
     docker compose -f docker-compose.ci.yml up --build
     ```

   - For local iterative development you can run backend and frontend independently.

   Backend (Python / FastAPI)

   ```bash
   # set a stub provider so the backend uses the local LLM/test stub
   export BACKEND_LLM_PROVIDER=stub
   # (optional) set AWS region or other env vars if you want to test real AWS paths
   cd backend
   # run with hot reload
   uvicorn backend.app.main:app --reload --port 8000
   # or use the Makefile convenience
   make backend-run
   ```

   Frontend (Next.js)

   ```bash
   cd frontend
   # ensure deps installed
   npm ci
   # point the frontend at the local backend if needed
   export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   npm run dev
   ```

🧪 Running tests

- Backend unit tests (pytest):

  ```bash
  cd backend
  pytest -q
  # or use the Makefile helper
  make backend-test
  ```

- Frontend tests (if present):

  ```bash
  cd frontend
  npm test
  ```

CI pipeline overview

- The repository includes GitHub Actions workflows to run tests and create preview artifacts. Key workflows:
  - .github/workflows/preview-test.yml — runs unit tests (backend), builds the frontend, and uploads artifacts (test logs, coverage) to help debugging PRs.
  - .github/workflows/preview-aws.yml — (optional) deploys ephemeral preview environments to AWS using Terraform when configured.

Workflows upload artifacts for failed runs and (optionally) persist preview URLs for reviewers. See the workflows directory for the exact steps and artifact names.

⚙️ Deployment overview

- Infrastructure is managed as Terraform scaffolding under infra/ (look for S3, Textract, OpenSearch, Cognito, API Gateway). The Terraform code is intentionally a minimal scaffold — review and harden before using in production.

- Secrets & credentials
  - For GitHub Actions: configure repository secrets such as AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, and any provider keys (e.g. BEDROCK_API_KEY or OPENAI_API_KEY) used by workflows.
  - For runtime: set environment variables in your hosting environment (COGNITO_USER_POOL_ID, BACKEND_LLM_PROVIDER, etc.).

- preview-aws.yml: a workflow that can provision or update preview stacks for PRs using Terraform and will store outputs as workflow artifacts or environment files for the frontend to consume.

🛠️ What’s implemented (MVP)

- Document ingestion pipeline scaffold (ingest CLI) with local parsing and chunking.
- Mock / stubbed auth (MockCognitoClient) for fast iteration locally.
- Embedding and retrieval stubs with an OpenSearch-like interface for vector search.
- FastAPI backend with RAG answer endpoint skeleton and health checks.
- Minimal Next.js frontend with chat UI placeholder to exercise the backend.
- DynamoDB recorder and Course/Syllabus in-memory fallback so app runs without AWS credentials.

🛣️ Roadmap (next priorities)

Planned improvements and features:

- Short term
  - Quizzes & in-app practice tests with result recording (DynamoDB + analytics) ✅ (scaffolded)
  - Improve RAG prompts & citation formatting
  - Role-based access & real Cognito integration

- Medium term
  - Group study / shared flashcards and collaborative sessions
  - Fine-grained ingestion (slide-level metadata, OCR improvements)
  - Better frontend UX: mobile responsiveness, saved sessions, export

- Long term
  - Automated syllabus mapping, course analytics, recommended study plans
  - Production-grade observability, quotas, and cost controls for LLM usage

🤝 Contributing

Thank you for your interest! We welcome small, focused PRs with tests and changelog notes. Before opening a PR:

- Run backend and frontend tests locally.
- If touching infra, include `terraform plan` output and mark PRs clearly.
- Follow the contributor guidance in CONTRIBUTING.md: ./CONTRIBUTING.md

If you plan to work on a bigger change, open an Issue first to align on design.

📜 License

This repository is provided under the MIT license. Replace this placeholder with your chosen license as needed.

----

If anything is unclear while setting up locally, open an Issue with your OS, error logs and the step that failed and maintainers will help. Happy building! 🎓✨
