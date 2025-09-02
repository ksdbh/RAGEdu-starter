# AWS integrations

Lists AWS services the scaffold is designed to use and integration notes.

Services used

- S3 — document storage (uploaded PDFs & attachments)
- Textract — OCR & structured extraction for PDFs (optional)
- Cognito — authentication (user pools) or use MockCognitoClient locally
- OpenSearch — vector index & metadata search (or OpenSearch Serverless)
- DynamoDB — lightweight recording (optional)

Integration notes

- Textract: prefer asynchronous job model for large documents and use S3 for inputs/outputs.
- OpenSearch: use knn_vector mappings or OpenSearch vector plugin. If you use OpenSearch Serverless, map dims accordingly.

Terraform pointers

- Look for infra/terraform files. Ensure proper lifecycle and least-privilege roles for Lambda/API Gateway.

Secrets and credentials

- Store Bedrock/OpenAI keys in AWS Secrets Manager or infrastructure CI secrets.

Where to edit

!!! info "Where to edit"
- Integration code: infra/ and backend/app/
- Ingestion entrypoint: backend/app/ingest.py

<!-- TODO: Add concrete Terraform module examples: owner @infra-team, path infra/ -->
