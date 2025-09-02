# IAM guidance for AWS resources

Principles

- Principle of least privilege: grant only the actions and resources required.
- Separate roles for ingestion (Textract, S3) and runtime (OpenSearch, LLM).

Recommended roles

| Role | Purpose | Example actions |
|------|---------|-----------------|
| IngestRole | Textract jobs, S3 read/write | s3:GetObject, s3:PutObject, textract:StartDocumentTextDetection, textract:GetDocumentTextDetection |
| APIExecutionRole | API access to OpenSearch & secrets | es:ESHttpPost, es:ESHttpGet OR appropriate OpenSearch permissions; secretsmanager:GetSecretValue |
| CI/CDRole | Terraform deploys | sts:AssumeRole, iam:PassRole (careful) |

Policy examples

!!! note "Example"
    Provide least-privilege policies in infra/iam/*.tf. <!-- TODO: infra/iam policy skeleton: owner @infra-team -->

Where to edit

!!! info "Where to edit"
- IAM guidance: docs/aws/iam.md
- Terraform IAM modules: infra/iam/
