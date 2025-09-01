# RAGEdu — AWS RAG Study Companion (Starter)

This repo is wired so an assistant bot can open PRs on command (via issue/PR comments) and run nightly error-log triage. You can keep it **PR-only** or enable **auto-merge on green**.

## Quick start

1. **Create the repo on GitHub** and push these files.
2. In repo **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `OPENAI_API_KEY`: your OpenAI API key.
   - (Optional) `SENTRY_TOKEN`, `DATADOG_API_KEY` if you want external log triage.
   - (Optional) `GH_AUTOMERGE_PAT`: a fine-scoped PAT (repo) to allow auto-merge (only if you opt in).
3. (Optional, safer) Add a **CODEOWNERS** file and branch protections so PRs require review.
4. In any PR or Issue, comment commands like:
   - `/scaffold Next.js + FastAPI skeleton for RAGEdu`
   - `/gen Add RAG retrieval endpoint with citations`
   - `/fix Resolve mypy/flake8 failures`
5. Nightly log triage runs on a cron. See `.github/workflows/scan-logs.yml`.

### What’s inside

- **.github/assistant.mjs** — tiny bot that reads repo context, calls the model, writes edits, opens PRs.
- **Workflows** — triggers for comment commands and nightly triage.
- **Backend** — FastAPI skeleton with a placeholder `/health` and a `/rag/answer` stub.
- **Frontend** — Next.js minimal UI with auth placeholder and a simple chat pane.
- **Infra (Terraform)** — S3/DynamoDB/OpenSearch Serverless/Cognito/API Gateway/Lambda scaffolding (minimal stubs).

> Production notes: prefer PR-only mode; require checks; never grant write-to-main unless in a sandbox.
