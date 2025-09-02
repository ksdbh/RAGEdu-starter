# Chunking

Chunking takes long text (pages) and splits into passages suitable for embedding and retrieval.

Reference implementation

The repository includes a chunker in backend/app/ingest.py:

- semantic_chunk_text(text, max_tokens=800, overlap_tokens=100) -> List[Chunk]
- chunk_pages(pages: Iterable[str], course_id, max_chars=1000) -> List[dict]

These functions produce chunks with metadata fields: course_id, page, length, section.

Rules & recommendations

- Target chunk size: 500–1000 characters (or ~256–800 tokens depending on embedding model).
- Overlap: 50–200 tokens to preserve context across chunk boundaries.
- Keep explicit metadata (page number, section heading) so frontend can show citations.

Where to edit

!!! info "Where to edit"
    Source: docs/rag/chunking.md
    Implementation: backend/app/ingest.py
    Tests: backend/tests/test_ingest.py (add if missing)
