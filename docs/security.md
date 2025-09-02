# Security posture

Summary

- Secrets: do not commit keys. Use AWS Secrets Manager, SSM Parameter Store, or GitHub Actions secrets.
- AuthN/Z: Cognito for production; MockCognitoClient for dev/test.
- Data handling: redact sensitive PII at ingestion time if required.

Practical rules

1. Never check in API keys or credentials.
2. Use environment variables or mounted secrets for runtime.
3. Limit LLM output exposure; log inputs/outputs selectively and avoid storing user secrets.

Adversarial inputs

- Validate and sanitize user-supplied instructions before sending to LLMs.
- Apply guardrails (see docs/rag/guardrails.md).

Where to edit

!!! info "Where to edit"
- Security notes: docs/security.md
- Auth implementation: backend/app/auth.py
- Guardrails: backend/app/rag.py
