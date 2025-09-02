# Embeddings

Embedding service responsibilities

- Produce dense vectors for each chunk text.
- Use deterministic encoding for reproducible test results (stubs use hashing).

Providers

- stub: local deterministic StubEmbeddings (backend/app/ingest.py)
- openai: OpenAI text-embedding-3-small or similar
- bedrock: Amazon Bedrock Titan embeddings

Decision checklist

- Choose dimensions consistent with chosen provider (1536 for many models; stub uses a small dim configurable value).
- Normalize or not: keep vector normalization consistent across index & queries.

Where to edit

!!! info "Where to edit"
    Source: docs/rag/embeddings.md
    Stub: backend/app/ingest.py::StubEmbeddings
    Provider wiring: backend/app/rag.py (or provider adapter module)
