# Deployment

This page outlines the deployment model and recommended steps for releasing to staging and production.

Overview

- Infrastructure: Terraform under infra/ (S3, OpenSearch, Cognito, API Gateway). Review and harden before applying.
- Application: Backend container (Docker) deployable to ECS/Fargate or other container hosts. Frontend built static assets served via CDN.

CI/CD recommendations

- Use GitHub Actions to run tests, build images, and deploy. Keep secrets in GitHub repository or organization secrets.
- Protect default branch: require PR reviews and passing CI.

Step-by-step (example)

1. Build and test on PR
  - Run backend unit tests (pytest)
  - Build frontend (next build)
2. Terraform plan for staging
  - terraform init && terraform plan -var='env=staging'
3. Apply infrastructure (staging)
  - terraform apply -auto-approve
4. Deploy backend (example ECS)
  - Build Docker image
  - Push to registry
  - Update service task definition with new image
5. Validate end-to-end tests
  - Smoke tests hitting /health and /rag/answer

Rollback

- Keep previous task definitions in ECS. For DB migrations, use backward-compatible schema changes.

Where to edit

!!! info "Where to edit"
- Deployment docs: docs/deployment.md
- Terraform: infra/
