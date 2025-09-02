# Retrieval

Retrieval responsibilities

- Query vector store for top-k similar chunks.
- Return passages with scores and metadata for prompt composition.

Reference implementation

- backend/app/rag.py — contains retrieval and reranking functions (if present). If missing, implement a retrieval adapter that:
  - accepts query text and top_k
  - computes embedding for query
  - calls OpenSearch/kNN search
  - returns a list of passages with metadata and score

Where to edit

!!! info "Where to edit"
    Source: docs/rag/retrieval.md
    Implementation: backend/app/rag.py
    Index creation: backend/app/ingest.py::create_opensearch_index

Tests

- backend/tests/test_rag.py — assert retrieval returns expected fields and that the RAG flow composes a prompt using top-k passages.
