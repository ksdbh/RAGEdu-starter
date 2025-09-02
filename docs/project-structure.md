# Project structure

Concrete file layout (top-level)

- backend/ — FastAPI backend, ingestion CLI, tests
  - backend/app/ — Python package (FastAPI app)
    - main.py — FastAPI app and routes
    - ingest.py — ingestion and chunking helpers
    - rag.py — retrieval / answer composition (TODO: ensure present)
    - auth.py — mock & real Cognito client
    - db.py — course & syllabus store
  - tests/ — pytest tests
- frontend/ — Next.js frontend
- infra/ — Terraform scaffolding (S3, Cognito, OpenSearch)
- docs/ — MkDocs Material documentation (this site)

Common commands

- Backend dev: uvicorn backend.app.main:app --reload --port 8000
- Backend tests: cd backend && pytest -q
- Frontend dev: cd frontend && npm run dev

Where to edit

!!! info "Where to edit"
    Source: docs/project-structure.md
    Owner: maintainers listed in CODEOWNERS
