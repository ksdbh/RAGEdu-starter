# Local PDF → course search

This is the implemented offline reference path as of October 30, 2026. It uses SQLite FTS5 keyword search and quotes actual passages. It does not call an LLM, compute semantic embeddings, or connect to AWS.

## Run it

With backend requirements installed, from the repository root:

```sh
python -m backend.app.ingest backend/examples/graphs.pdf --course CS101
RAGEDU_MODE=local python -m uvicorn backend.app.main:app --reload --port 8000
```

Start the frontend with `cd frontend && npm ci && npm run dev`. Select CS101 on home and ask “What does Dijkstra require?” The two-page synthetic fixture cites `graphs.pdf`, page 1. The alternative `/demo` route uses the same UI.

Use any readable text PDF in place of the fixture. `--title` overrides its display title; `--max-chars` sets the passage character budget (default 1000). Blank pages are skipped without renumbering later pages. Oversized lines are split; chunking is character-based, not semantic/token-aware.

The CLI defaults to `data/courses.sqlite3`. Override with `--index` or `RAGEDU_INDEX_PATH`. The API must use the same path via `RAGEDU_INDEX_PATH`. Relative paths resolve from the process working directory; use absolute paths when running from another directory. The CLI prints JSON with course/document/source/page/passage counts and exits nonzero on failure.

## Storage and retrieval behavior

- SHA-256 of the PDF bytes identifies a document. Course plus document identity determines replacement: identical bytes in the same course are reindexed atomically, without duplicate passages; changed bytes remain a separate document. No deletion/version-management UI is implemented.
- Stored passages include course, document/chunk IDs, filename (not full local path), page, section, title, and text. The SQLite file contains course content; keep it local and out of Git. It is ignored by default.
- Read-only searches never create a missing index. A missing index yields an empty course list/insufficient evidence. A corrupt or incompatible index yields HTTP 503 rather than sample/demo answers.
- Queries are tokenized, common English stopwords omitted, and keyword matches ranked by SQLite BM25 inside the requested course. A bounded token-coverage signal feeds the guardrail (threshold 0.25). This score is not semantic similarity or answer correctness. The simple English stopword/tokenization choices need evaluation for multilingual materials.
- The selected passages are quoted with actual page/source citations. No explanation is synthesized. No match returns `metadata.status: "insufficient_evidence"` and no citations. Selecting a different course clears the prior UI response.
- A running API reads fresh connections so new imports are immediately searchable. Reload the UI to refresh the course list. This is course filtering, not a permissions system; local study endpoints are unauthenticated.

## HTTP contract

`GET /rag/status` returns `mode`, `courses`, `retrieval`, and `generation`. Local courses contain `course_id`, `documents`, and `passages` counts.

`POST /rag/answer` accepts one of `query` or `question`, optional `top_k` (strict integer 1..20, default 5), and `course_id` (required in local mode). Queries are nonempty and limited to 1000 characters. The older `question` alias retains its 400 validation errors; invalid `query` uses 422.

Responses contain `answer`, `citations`, and `metadata`. Local citations include title/page/snippet/score/source/document_id/chunk_id/course_id/section. Metadata identifies `mode: "local"`, `retrieval: "keyword"`, `generation: "source_excerpts"`, and status. An unknown course is an ordinary no-match result. Local runtime misconfiguration/storage faults do not fall back to simulated sources.

## Boundaries

This CLI is intended for trusted local text PDFs. Encrypted and image-only PDFs fail clearly; OCR is not implemented. The file-size limit is 25 MiB; this is not a resource-isolated parser for hostile uploads. There is no PDF-serving endpoint, upload UI, semantic index, external provider integration, course authorization, or cloud persistence in this path. Decide those requirements before extending it to a hosted service.

See the [handoff](../changelog.md) for tests, verification, and the next milestone.
