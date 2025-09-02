# Architecture

This page describes the high-level architecture and design decisions for EduRAG. The goal is clarity for engineers making changes to ingestion, indexing, or the QA pipeline.

Overview

- Ingestion: PDFs / slides are uploaded to S3 (or processed locally). Text is extracted (Textract or local parser) and passed to chunking.
- Chunking: semantic & page-aware chunking, metadata enrichment (course_id, page, section).
- Embeddings: text chunks are embedded with a vector provider (Bedrock or OpenAI).
- Indexing: vectors are stored in OpenSearch (or an emulated vector index for local dev).
- Retrieval + QA: FastAPI endpoint fetches top-k passages, composes a prompt, calls LLM, returns a grounded answer with citations.

Decision table: key design choices

| Area | Choice in scaffold | Why | Where to change |
|------|--------------------|-----|-----------------|
| Embeddings provider | Stub / Bedrock / OpenAI | Keep local fast iteration, allow production swap | backend/app/ingest.py, backend/app/rag.py <!-- TODO: confirm -->
| Vector store | OpenSearch (knn_vector) | Familiar, AWS supported | infra/ (terraform), backend/app/ingest.py
| Auth | Cognito (real) or MockCognitoClient for dev | Cognito for production, Mock for dev/test | backend/app/auth.py

Integration diagram (text)

Client -> API (FastAPI) -> OpenSearch (vector search)
                 \-> LLM provider (Bedrock/OpenAI)

Security boundary

- LLM provider keys and AWS credentials are secrets and must be stored in a secrets manager (AWS Secrets Manager or GitHub Actions secrets for CI).

Where to edit

!!! info "Where to edit"
- Architecture notes: docs/architecture.md
- Source code: backend/app/
- Ingest pipeline: backend/app/ingest.py
