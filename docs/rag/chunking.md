# Chunking

This page documents the chunking strategies used by the scaffold.

Functions of interest

- semantic_chunk_text(text, max_tokens=800, overlap_tokens=100)
  - Purpose: simple sliding-window chunker for long text.
  - Returns: List[Chunk] dataclasses with start/end offsets.
  - Where to edit: backend/app/ingest.py

- chunk_pages(pages: Iterable[str], course_id: str, max_chars: int = 1000)
  - Purpose: page-aware chunking that prefixes chunks with page/section metadata.
  - Output: list of dicts {text, metadata, course_id, page, length}
  - Where to edit: backend/app/ingest.py

Best practices

- Choose chunk size so that prompt + context fits model input limits.
- Use overlap_tokens to preserve continuity across chunk boundaries.

Where to edit

!!! info "Where to edit"
- Chunking code: backend/app/ingest.py
- Tests: backend/tests/test_ingest.py <!-- TODO: add or update -->
