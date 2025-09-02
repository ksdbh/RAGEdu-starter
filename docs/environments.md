# Environments

Supported environments and differences

- dev (local): Uses MockCognitoClient, in-memory DB, and stubbed embedding/LLM providers. No real AWS credentials required.
- staging: Intended to use real AWS services in a sandbox account. Configure Cognito, S3, and OpenSearch. Use smaller instance sizes and feature flags for lower cost.
- prod: Hardened configuration, stricter IAM, monitoring, and backups. Use real Bedrock/OpenAI keys and production OpenSearch clusters.

Environment variables (most important)

| Env var | Purpose | Notes |
|---|---|---|
| AWS_REGION | AWS region | e.g. us-east-1 |
| COGNITO_USER_POOL_ID | If present, RealCognitoClient is used | Leave unset in local dev |
| OPENAI_API_KEY | Optional; used if OPENAI provider selected | Store in secret manager for prod |
| BACKEND_LLM_PROVIDER | Provider selection (stub, openai, bedrock) | Default: stub |
| USE_IN_MEMORY_DB | 1 = in-memory course store | Default for tests/dev |

Secrets handling

!!! warning "Secrets"
    Never commit credentials or keys. Use GitHub secrets for CI and AWS Secrets Manager or Parameter Store in prod.

Where to edit

!!! info "Where to edit"
    Source: docs/environments.md
    Code: backend/app/auth.py, backend/app/db.py
