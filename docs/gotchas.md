# Common gotchas

- Token vs Bearer: FastAPI HTTPBearer expects the token after "Bearer ". In local mock tests you can pass bare tokens in Authorization header.
- Vector dims mismatch: When creating OpenSearch index ensure the embedding dim matches the embeddings you write.
- Real AWS vs stubs: setting COGNITO_USER_POOL_ID or AWS_ENDPOINT_URL will change behavior — review logs carefully.

Where to edit

!!! info "Where to edit"
- Gotchas: docs/gotchas.md
- Relevant code: backend/app/auth.py, backend/app/ingest.py
