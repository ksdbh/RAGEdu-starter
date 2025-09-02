# AWS Integrations

This project uses (or plans to use) the following AWS services:

- S3 — document storage (PDFs/slides)
- Textract — OCR / text extraction (optional; local parser allowed)
- OpenSearch — vector index (or hosted OpenSearch Service)
- Cognito — authentication / user pools
- (Optional) Bedrock / OpenAI — LLM and embeddings

Region guidance

- Preferred region: us-east-1 (example). Choose a region close to your users and LLM provider availability.

Integration notes

!!! note
    The repo contains stub implementations for many AWS integrations. Replace stubs with production clients and secure credentials.

Where to edit

!!! info "Where to edit"
    Source: docs/aws/integrations.md
    Code: backend/app/ingest.py, backend/app/rag.py, infra/
