# Architecture

This page documents the high-level architecture and runtime flow used by EduRAG.

Overview

- Ingestion: PDFs/slides uploaded to S3 (or local upload) → OCR/parse (Textract or PDF parser) → chunker → embedder → vector index (OpenSearch)
- Query time: Client → FastAPI RAG API → vector store (OpenSearch) → LLM (Bedrock/OpenAI) → client

Decision table (why components were chosen)

| Concern | Choice (scaffold) | Rationale |
|---|---:|---|
| Embeddings | Bedrock / OpenAI (stub available) | Provider-agnostic; stub included for local dev |
| Vector store | OpenSearch (or stub) | Familiar open-source vector-capable store; Terraform scaffold included |
| AuthN/Z | Cognito (mock in dev) | AWS-native auth; mock client for local dev |

Runtime flow

1. Upload document (S3 or direct upload).
2. Extract text (Textract or local PDF parser).
3. Chunk pages into semantic passages with metadata.
4. Compute embeddings for each chunk and index vectors.
5. At query time, retrieve top-k vectors, build prompt, call LLM, format answer with citations.

Where to edit

!!! info "Where to edit"
    Source: docs/architecture.md
    Key modules: backend/app/ingest.py, backend/app/rag.py, backend/app/main.py
