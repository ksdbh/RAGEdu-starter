# Monitoring

Key signals to observe

- API: 5xx rate, 4xx rate, latency p95/p99
- OpenSearch: query latency, CPU/memory, queue length
- LLM usage: tokens consumed, errors, rate limits

Dashboards & alerts

- Create dashboards for API and OpenSearch.
- Alerts: API error spike (>= 5% 5xx over 5m), LLM errors > 5 in 5m, OpenSearch cluster red status.

Where to edit

!!! info "Where to edit"
    Source: docs/operations/monitoring.md
    Code: infra/monitoring (if present)
