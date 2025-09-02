# Ingestion

Ingestion pipeline responsibilities

1. Extract text from uploaded files (Textract or PDF parser).
2. Normalize whitespace and line breaks.
3. Chunk text into passages with metadata (page, section, course_id).
4. Compute embeddings and index vectors.

Quick ingest checklist (developer)

- Confirm source file accessible (S3 or local path).
- Run extraction step (Textract or PDF parser). See TODOs below.
- Use chunk_pages (backend/app/ingest.py) to build chunks.
- Use embeddings client to encode and index.

!!! note "Local dev"
    The project includes a local ingest CLI at backend/app/ingest.py. Use `python -m app.ingest path/to/file.pdf --course CS101` from the backend/ folder.

Where to edit

!!! info "Where to edit"
    Source: docs/rag/ingestion.md
    Ingest logic: backend/app/ingest.py
    CLI: backend/app/ingest.py
