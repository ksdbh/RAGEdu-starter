# RAG Overview

Retrieval-Augmented Generation (RAG) combines a retrieval component (vector search over documents) with a generative LLM to produce answers grounded in source documents.

Components

- Ingest: parse PDFs/slides to text and split into chunks with metadata.
- Embed: compute vector embeddings for chunks.
- Index: store vectors in OpenSearch or vector DB.
- Retrieve: find top-k relevant passages.
- Compose: build a prompt including retrieved passages and call the LLM.

Best practices

- Keep chunks small enough for clear citations (~500–1,000 chars) but large enough to preserve context.
- Return sources with page/section metadata to allow UI citations.

Where to edit

!!! info "Where to edit"
    Source: docs/rag/overview.md
    Code: backend/app/ingest.py, backend/app/rag.py
