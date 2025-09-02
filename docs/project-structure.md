# Project structure

Short prescriptive tree of important paths and responsibilities.

Top-level layout

- backend/ — FastAPI application and ingestion logic
  - backend/app/
    - main.py — FastAPI app entrypoint and route registrations
    - auth.py — Cognito / Mock auth helpers
    - ingest.py — ingestion, chunking, and embedding stubs
    - rag.py — retrieval and QA orchestration (answers) <!-- TODO: create/verify -->
    - db.py — course & syllabus store
  - requirements.txt, requirements-dev.txt
- frontend/ — Next.js chat UI
- infra/ — Terraform scaffolding for S3, Textract, OpenSearch, Cognito, API Gateway
- docs/ — this documentation (MkDocs)

Owners & edit points

| Area | Path | Owner |
|------|------|-------|
| Backend entry | backend/app/main.py | @backend-owner <!-- TODO: replace -->
| Ingest pipeline | backend/app/ingest.py | @data-team <!-- TODO: replace -->
| RAG logic | backend/app/rag.py | @ml-team <!-- TODO: replace -->
| Terraform infra | infra/ | @infra-team <!-- TODO: replace -->

Where to edit

!!! info "Where to edit"
- Source: backend/app/
- Docs: docs/project-structure.md
