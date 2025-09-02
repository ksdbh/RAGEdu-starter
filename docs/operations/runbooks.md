# Runbooks

On-call runbook for common incidents.

Incident: API 500s

1. Check backend logs (CloudWatch / container logs).
2. Validate /health endpoint.
3. If recent deploy, roll back to prior task definition.

Incident: Index not returning results

1. Verify OpenSearch cluster health.
2. Check index mappings & dims.
3. Confirm embeddings were created and vectors stored.

Pager escalation

- Level 1: engineer on-call
- Level 2: platform lead
- Level 3: infra owner

Where to edit

!!! info "Where to edit"
- Runbook: docs/operations/runbooks.md
- Monitoring config: docs/operations/monitoring.md
