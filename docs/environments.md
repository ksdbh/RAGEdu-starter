# Environments

This project targets three typical environments: dev, staging, prod. The scaffold provides patterns and environment-specific differences.

Environment differences

- dev
  - Local services or stubs (MockCognitoClient, StubEmbeddings, in-memory DB)
  - No production secrets; set OPENAI_API_KEY or other provider keys only if testing.
  - Useful for iteration and unit tests.
- staging
  - Mirrors production infrastructure in AWS using a non-production AWS account/namespace.
  - Real S3, OpenSearch, Cognito; LLM provider can be real or limited.
- prod
  - Hardened, monitoring, stricter IAM, cost controls.

Configuration sources

- Environment variables (recommended for secrets in dev):
  - AWS_REGION
  - COGNITO_USER_POOL_ID
  - OPENAI_API_KEY or BEDROCK credentials
  - BACKEND_LLM_PROVIDER
  - AWS_ENDPOINT_URL (for localstack / test endpoints)

Deployment pointers

- Use infra/ Terraform to create resources for staging/prod (see docs/aws/integrations.md and infra/).

Ownership and runbooks

- Each environment should have owners and runbooks (see operations/runbooks.md). Tag Terraform states and SSM/ParameterStore secrets by environment.

Where to edit

!!! info "Where to edit"
- Environment docs: docs/environments.md
- Infra code: infra/
