# Contributing & Local Development

Thanks for contributing to RAGEdu — this doc describes how to get the project running locally (backend, frontend, infra), useful Makefile targets, and a simple architecture diagram.

Prerequisites
- Git
- Python 3.11
- Node 20 / npm
- Docker (recommended for devcontainer / optional for local infra like LocalStack)
- Terraform (if you plan to manage the provided infra)
- AWS CLI + credentials (only required if interacting with real AWS services)

Using the devcontainer
- This repo includes a VS Code devcontainer (.devcontainer/devcontainer.json). When opening in the devcontainer, the postCreateCommand will run:
  pip install -r backend/requirements.txt && cd frontend && npm i

Quick overview of the stacks
- Backend: FastAPI (backend/app) — provides /health, auth helpers, ingestion CLI and RAG stubs.
- Frontend: Next.js (frontend) — minimal UI for chat and auth placeholder.
- Infra: Terraform scaffolding (infra/) — S3/Textract/OpenSearch/Cognito stubs (see README).

Local backend development

1. Create and activate a Python venv (optional but recommended):
   python -m venv .venv
   source .venv/bin/activate

2. Install Python dependencies:
   pip install -r backend/requirements.txt

3. Environment variables (optional for local dev):
   - OPENAI_API_KEY — required for any code paths using OpenAI.
   - AWS_REGION, COGNITO_USER_POOL_ID — if omitted the scaffold will use local/mock fallbacks.

4. Run the API locally (hot reload):
   uvicorn backend.app.main:app --reload --port 8000

5. Authentication (local / mock tokens):
   The scaffold provides a MockCognitoClient. You can test endpoints using the following bearer tokens:
   - Student: Authorization: Bearer student_token
   - Professor: Authorization: Bearer prof_token
   - Admin (alias): Authorization: Bearer admin_token
   - Custom mock: Authorization: Bearer "mock:alice|professor"

   Example curl:
   curl -H "Authorization: Bearer student_token" http://localhost:8000/whoami

6. Ingestion CLI (local):
   The ingest CLI lives in backend/app/ingest.py. To run it from the repository root (recommended from backend/):
   cd backend
   python -m app.ingest path/to/sample.pdf --course CS101

Local frontend development

1. Install JS deps:
   cd frontend
   npm ci

2. Run dev server (Next.js default port 3000):
   npm run dev

3. If the frontend needs to talk to the local backend, ensure the backend is running and adjust the frontend environment (frontend/.env.local or the dev server proxy) as needed.

Local infra (Terraform)

- The repo contains Terraform scaffolding (look for an infra/ or terraform/ directory). These files are minimal stubs to show the intended resources (S3/Textract/OpenSearch/Cognito/API Gateway/Lambda).
- You will need AWS credentials and proper AWS access to apply the real infrastructure.
- For quick experimentation you can use LocalStack, but note that services like Textract and OpenSearch Serverless may not be fully supported by LocalStack.

Common Terraform commands
- terraform init
- terraform plan
- terraform apply -auto-approve
- terraform destroy -auto-approve

Makefile targets (recommended)

This repository includes a Makefile to simplify common dev tasks. From the repo root:

- make help                 # show available targets
- make devcontainer-setup   # run the same steps as the devcontainer postCreateCommand

Backend targets
- make backend-install      # create venv & install backend deps (simple convenience)
- make backend-run          # run the FastAPI app with uvicorn on port 8000
- make backend-test         # run pytest in the backend directory
- make ingest FILE=... [COURSE=...] # ingest a PDF via the scaffold (calls backend CLI)

Frontend targets
- make frontend-install     # cd frontend && npm ci
- make frontend-dev         # cd frontend && npm run dev
- make frontend-build       # cd frontend && npm run build

Infra targets (run terraform commands if infra/ exists)
- make infra-plan
- make infra-apply
- make infra-destroy

Notes on working with real AWS
- If you plan to connect the scaffold to real AWS services (Textract, S3, Bedrock/OpenAI, OpenSearch), ensure your AWS credentials are configured (environment variables, profile, or role).
- The scaffold contains many "stub" implementations (e.g. BedrockEmbeddingClientStub, OpenSearchIndexerStub, MockCognitoClient). Replace these with production clients carefully and consider secrets and IAM least-privilege.

Architecture diagram

Below is a high-level flow diagram for the typical ingestion + query path. This uses Mermaid syntax for rendering in supported viewers.

```mermaid
flowchart LR
  S3[S3 (uploaded PDFs / documents)] --> Textract[Amazon Textract]
  Textract --> Chunking[Semantic chunking (parse & chunk text)]
  Chunking --> Embedding[Embedding service (Bedrock / OpenAI)]
  Embedding --> OpenSearch[OpenSearch (vector index)]
  OpenSearch --> RAG[RAG API / QA service]

  classDef aws fill:#f3f4f6,stroke:#111827
  class S3,Textract aws

  %% Notes
  click S3 "https://aws.amazon.com/s3/" "S3"
  click Textract "https://aws.amazon.com/textract/" "Textract"
```

RAG query flow (runtime)
- Client -> RAG API -> OpenSearch (vector similarity) -> RAG API composes prompt with top-k passages -> LLM (OpenAI/Bedrock) -> Response with citations

Testing and linting
- Backend tests: cd backend && pytest
- Frontend tests: cd frontend && npm test (if present)
- Linting / formatting: see Makefile targets but tools may not be configured in the scaffold; add your preferred linters/formatters.

Contributing guidelines (short)
- Prefer small focused PRs with a single change.
- Run backend and frontend tests locally before opening a PR.
- If your change affects infrastructure, include Terraform plan output and mark the PR with "infra".

If you need help getting set up, open an Issue with the details of your OS and what step failed and someone will help.
