# Retrieval & QA

This document explains how retrieval is performed and where the QA orchestration lives.

Key file

- backend/app/rag.py — primary orchestration for retrieval and answer composition.

Typical flow inside answer handler (answer_query)

1. Validate request
2. Query vector index (OpenSearch) for top_k nearest neighbors
3. Fetch chunk texts and metadata
4. Compose prompt using a deterministic template with the top passages
5. Call LLM provider with prompt
6. Post-process LLM output and return answer + sources

Where to edit

!!! info "Where to edit"
- Retrieval code & prompt: backend/app/rag.py
- Index query helpers: backend/app/ingest.py (index client) or dedicated indexer module
- Tests: backend/tests/test_rag.py

Reference (functions to look for)

- answer_query(request) — orchestrator
- search_index(query_vector, top_k) — index query helper (may be named differently)

<!-- TODO: If backend/app/rag.py does not exist, create scaffolding: owner @ml-team -->
