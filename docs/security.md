# Security

High-level security posture

- AuthN: Cognito (mock in dev). Use RealCognitoClient in production and validate JWTs.
- Secrets: store in GitHub Actions secrets, AWS Secrets Manager, or Parameter Store. Do not commit to git.
- Data: redact sensitive PII before storing embeddings or sending to external LLMs where necessary.

Recommendations

- Audit LLM prompts for data leaks.
- Use rate limits and quota controls to mitigate cost & abuse.
- Enable VPC access to OpenSearch and restrict ingress.

Where to edit

!!! info "Where to edit"
    Source: docs/security.md
    Code: backend/app/auth.py, infra/
