# Troubleshooting

Common issues and steps

- Health checks failing: inspect backend logs (uvicorn) and dependency availability (OpenSearch reachable?).
- Auth failures: ensure COGNITO_USER_POOL_ID is set for real Cognito. For local dev, use mock tokens.
- Slow responses: check OpenSearch query times and LLM provider throttling.

Where to edit

!!! info "Where to edit"
    Source: docs/operations/troubleshooting.md
    Code: backend/app/main.py, backend/app/rag.py
