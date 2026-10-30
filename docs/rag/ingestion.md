# Ingestion

The active local path is **text PDF → pypdf extraction → bounded page passages → SQLite FTS5**. It does not compute semantic embeddings, upload to S3, or call Textract. See the [complete local guide](../guides/local-course-search.md).

From repository root, after installing backend requirements:

```sh
python -m backend.app.ingest backend/examples/graphs.pdf --course CS101
```

Use `--index` (or `RAGEDU_INDEX_PATH`) to choose the SQLite file, `--title` for the display title, and `--max-chars` for passage length. The API must use that same index path in `RAGEDU_MODE=local`.

Original page numbers survive blank-page omission. Passages carry source filename, content-based document identity, chunk identity, course/page/section metadata, and text. Identical-byte imports into the same course atomically replace passages without duplicates. Changed bytes form a distinct document; index version/deletion management remains future work.

Encrypted PDFs, image-only/empty PDFs, unreadable files, and invalid input fail nonzero instead of reporting a successful ingest. OCR is not implemented. The size limit is 25 MiB. This is a trusted local CLI, not a hardened public upload service.

Code: `backend/app/ingest.py` and `backend/app/local_index.py`. Historical OpenSearch mapping/hash-embedding helpers remain separate scaffolding; they are not used in this path. See the [handoff](../changelog.md) before choosing cloud/semantic integrations.
