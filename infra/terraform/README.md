# Terraform — infra/terraform

This folder contains Terraform modules and a small root module for provisioning the minimal infra for the project:
- S3 bucket for docs
- DynamoDB tables for users, courses, and study events
- OpenSearch Serverless collection (vector-ready placeholder)

Quick usage

1. Install Terraform (>= 1.6.0) and configure AWS credentials (e.g. via AWS CLI environment variables).

2. Initialize the working directory:

   terraform init

3. Preview changes:

   terraform plan -var="project=myproj" -var="region=us-east-1"

4. Apply changes:

   terraform apply -var="project=myproj" -var="region=us-east-1"

Notes / TODO

- Remote state: this repo currently does not configure a remote backend. For team usage you should configure a remote backend (S3 backend + DynamoDB table for state locking) in a separate backend configuration or via Terraform Cloud. Example backend to add in production:

  terraform {
    backend "s3" {
      bucket = "<state-bucket>"
      key    = "infra/terraform/terraform.tfstate"
      region = "us-east-1"
      dynamodb_table = "<state-lock-table>"
    }
  }

- Security / production hardening to consider:
  - S3: enable encryption, block public access, lifecycle rules
  - DynamoDB: add GSIs, point-in-time recovery, autoscaling if not using PAY_PER_REQUEST
  - OpenSearch: configure security configs, network (VPC access), capacity

- This is scaffolding to be iterated on. Each module is intentionally minimal to make it easy to extend.
