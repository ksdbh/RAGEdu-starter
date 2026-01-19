# Getting Started — run EduRAG locally

This page walks you from a fresh clone to “first answer with citations” as quickly as possible.

## Prerequisites

- Git
- Python 3.11
- Node 20 + npm
- Docker (optional, but useful for the full stack via Docker Compose)

## 1. Clone the repository

```bash
git clone https://github.com/ksdbh/RAGEdu-starter.git
cd RAGEdu-starter
```

## 2. Choose your setup path

Use the tabs below to pick the setup that best matches how you like to work.

=== "Local sandbox (recommended)"

This path runs everything directly on your machine.

1. **(Optional) create a virtualenv**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install backend dependencies**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Install frontend dependencies**

   ```bash
   cd frontend
   npm ci
   cd ..
   ```

4. **Run the backend (FastAPI)**

   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

5. **Run the frontend (Next.js)** in a second terminal:

   ```bash
   cd frontend
   export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   npm run dev
   ```

You now have:

- Backend at `http://localhost:8000` (see `/health`, `/whoami`, `/rag/answer`).
- Frontend at `http://localhost:3000` pointing to your local backend.

=== "Makefile helpers"

If you prefer a few convenience commands, use the repo Makefile from the root:

```bash
# one-time dependency setup
make devcontainer-setup  # installs backend + frontend deps

# backend
make backend-run         # uvicorn backend.app.main:app --reload --port 8000
make backend-test        # run pytest in backend/

# frontend
make frontend-dev        # next dev
```

This is functionally equivalent to the local sandbox path, but uses shorter commands.

=== "Docker Compose stack"

Use this if you want the backend, frontend, OpenSearch, and LocalStack running together using Docker containers.

```bash
# dev-style stack
docker compose -f docker-compose.dev.yml up --build

# or, to mirror CI more closely
# docker compose -f docker-compose.ci.yml up --build
```

This brings up:

- `backend` on port `8000`.
- `frontend` on port `3000`.
- `opensearch` on port `9200`.
- `localstack` on port `4566` for S3/DynamoDB stubs.

Stop the stack with `Ctrl+C` and `docker compose ... down` when done.

## 3. Mock auth tokens (local & CI)

For local development the backend uses a `MockCognitoClient`. You can hit protected endpoints using simple bearer tokens:

- `student_token` (role: `student`)
- `prof_token` (role: `professor`)
- `admin_token` (role: `professor` alias)
- `mock:alice|professor` (custom mock user)

Example request:

```bash
curl -H "Authorization: Bearer student_token" http://localhost:8000/whoami
```

## 4. Time to first answer

Once the backend is running you can call the RAG endpoint.

### Minimal happy-path request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  http://localhost:8000/rag/answer \
  -d '{"query": "What does this course cover?"}'
```

You should see a JSON response like:

```json
{
  "answer": "ANSWER based on retrieved docs: ...",
  "citations": [
    {"title": "Doc 1", "page": 1, "snippet": "Context A", "score": 0.9},
    {"title": "Doc 2", "page": 2, "snippet": "Context B", "score": 0.8}
  ],
  "metadata": {
    "top_k": 5,
    "course_id": null,
    "confidence": 0.9
  }
}
```

Behind the scenes, the backend is using a deterministic stub search client and stub LLM so this works without any external services.

## 5. Next steps

- To ingest real PDFs and build an index, see the [RAG ingestion docs](rag/ingestion.md) and the ingest CLI in `backend/app/ingest.py`.
- To understand the architecture and how to customize components, read [Architecture](architecture.md) and the [RAG Pipeline](rag.md).

---

!!! info "Where to edit"
    Source: `docs/getting-started.md`  
    Backend startup: `backend/app/main.py`  
    Ingest CLI: `backend/app/ingest.py`
