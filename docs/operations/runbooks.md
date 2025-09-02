# Runbooks

On-call runbook (quick)

1. Alert: RAG API errors / high latency
2. Check: CI/CD or deploy logs and CloudWatch/OpenSearch metrics
3. Rollback: revert to previous deployment via CI if recent change caused issue
4. Mitigate: scale up OpenSearch nodes or reduce LLM concurrency

Emergency contact & ownership

- Add team on-call contact here. <!-- TODO: fill CODEOWNERS and on-call rotation -->

Where to edit

!!! info "Where to edit"
    Source: docs/operations/runbooks.md
    Ops: infra/ and monitoring config
