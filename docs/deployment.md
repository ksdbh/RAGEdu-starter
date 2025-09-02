# Deployment

Short prescriptive steps for deploying to AWS (scaffold)

1. Review infra/ terraform code and upgrade from stubs to production-grade modules.
2. Configure Terraform variables and backend state storage (S3 + DynamoDB for locking).
3. Provide CI/CD credentials with least privilege for apply operations.
4. Run terraform init/plan/apply in infra/ after review and approvals.

CI/CD recommendations

- Use GitHub Actions with a separate deploy workflow for main -> prod.
- Put sensitive variables in environment secrets, reference them in workflows.

Rollback plan

- Keep terraform state backups and follow standard terraform rollback steps.
- For application changes, prefer blue/green or canary deploys.

Where to edit

!!! info "Where to edit"
    Source: docs/deployment.md
    Infra: infra/ (Terraform files)
