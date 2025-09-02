# How the assistant uses docs

Design intent

- The assistant composes answers from retrieved chunks. Documentation (course materials) is the canonical source for facts and citations.

Best practices for docs that feed retrieval

- Keep headings and section labels concise — chunking heuristics extract section names from uppercase headings and numbered lists.
- Attach page numbers and section metadata during ingestion so the assistant can cite exact sources.

Where to edit

!!! info "Where to edit"
- Assistant behavior: backend/app/rag.py
- Ingestion: backend/app/ingest.py
