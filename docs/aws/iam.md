# AWS IAM guidance

Principles

- Least privilege: give each runtime role only the permissions needed (S3 read/list, OpenSearch access, Cognito read groups).
- Separate roles per environment: dev/staging/prod each have separate IAM roles and policies.

Example policy snippets (high-level)

- S3 read-only access to specific bucket(s).
- OpenSearch: managed access via IAM policies or VPC access depending on deployment.
- Textract: Textract:StartDocumentTextDetection + S3 read for input/output.

!!! note
    For OpenSearch Serverless or AWS-managed OpenSearch, follow AWS docs for access methods (IAM roles, fine-grained access, or proxy lambda).

Where to edit

!!! info "Where to edit"
    Source: docs/aws/iam.md
    Infra: infra/ (Terraform IAM policy files)
