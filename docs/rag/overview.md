# RAG overview

This page explains the RAG pipeline implemented by EduRAG.

Pipeline stages

1. Ingestion: extract text from documents (Textract or local parser) and create pages.
2. Chunking: break pages into overlapping chunks with metadata (course_id, page, section).
3. Embeddings: convert chunks to vectors using the embedding provider.
4. Indexing: store vectors and metadata in OpenSearch.
5. Retrieval & QA: API fetches top-k chunks, composes prompt, calls LLM to synthesize an answer.

Design goals

- Ground answers in course materials with explicit citations.
- Be robust to missing AWS credentials by providing stubs for local dev.
- Keep LLM prompts minimal and deterministic where possible.

Where to edit

!!! info "Where to edit"
- Pipeline code: backend/app/ingest.py, backend/app/rag.py
- Tests: backend/tests/
