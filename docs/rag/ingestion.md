# Ingestion

This tutorial shows how to ingest a PDF or text corpus into the index.

High-level steps

1. Extract text from document (Textract or local parser).
2. Page-split and normalize newlines.
3. Chunk pages via chunk_pages or semantic_chunk_text.
4. Embed via embedding client and index into OpenSearch.

Local example (CLI)

The repository exposes an ingest CLI at backend/app/ingest.py. Example:

```bash
cd backend
python -m app.ingest path/to/file.pdf --course CS101
```

Implementation notes

- The function chunk_pages(pages, course_id=...) returns a list of dicts with text and metadata.
- The embedding client and indexer are pluggable; check backend/app/ingest.py for StubEmbeddings.

Where to edit

!!! info "Where to edit"
- Ingest code: backend/app/ingest.py
- Indexing: infra/ and backend/app/ingest.py
- Tests: backend/tests/test_ingest.py <!-- TODO: add tests -->
