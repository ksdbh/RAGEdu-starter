# Common Gotchas

- Stubs vs production: many components are intentionally stubbed (embeddings, Cognito). Replacing them requires wiring secrets and adjusting response shapes.
- Token limits: prompt + retrieved context may exceed LLM context window. Be conservative with top_k and chunk sizes.
- OpenSearch types: mapping for vector fields varies by OpenSearch version. Verify mapping before indexing.

Where to edit

!!! info "Where to edit"
    Source: docs/gotchas.md
    Fixes: backend/app/ingest.py, backend/app/rag.py, infra/
