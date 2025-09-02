# Troubleshooting

Quick troubleshooting checklist

- 401s: check token and whether MockCognitoClient is active. If COGNITO_USER_POOL_ID is set, switch to real Cognito.
- No search results: ensure documents were ingested, check index mapping and vector dims.
- LLM timeouts: check provider and network connectivity; reduce top_k or prompt size.

Logs to inspect

- Backend logs (application + uvicorn)
- OpenSearch logs
- LLM provider logs / request traces

Where to edit

!!! info "Where to edit"
- Troubleshooting docs: docs/operations/troubleshooting.md
