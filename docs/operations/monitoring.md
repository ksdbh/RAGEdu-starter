# Monitoring

Key metrics to monitor

- API latency and error rates (/rag/answer, /health)
- LLM provider latency and error rates (quota errors, 5xx)
- OpenSearch cluster health and query latency
- Ingestion pipeline failures (Textract job failures, S3 errors)

Dashboards & alerts

- Dashboard: API errors, 95/99 latency, top failing endpoints
- Alerts: error rate > 5% sustained for 5 minutes; OpenSearch status not green; LLM provider quota errors

Where to edit

!!! info "Where to edit"
- Monitoring docs: docs/operations/monitoring.md
- Dashboards: infra/monitoring/ or cloudwatch/ dashboards
