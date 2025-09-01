terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6.0"
}

provider "aws" {
  region = var.region
}

locals {
  // allow overriding the opensearch collection name; default to "${var.project}-vec" when omitted
  opensearch_collection_name = var.opensearch_collection_name != "" ? var.opensearch_collection_name : "${var.project}-vec"
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = var.bucket_name
  project     = var.project
  tags        = var.tags
}

module "dynamodb" {
  source  = "./modules/dynamodb"
  project = var.project
}

module "opensearch" {
  source          = "./modules/opensearch"
  collection_name = local.opensearch_collection_name
  project          = var.project
}

output "bucket" {
  description = "S3 docs bucket name"
  value       = module.s3.bucket_name
}

output "bucket_arn" {
  description = "S3 docs bucket ARN"
  value       = module.s3.bucket_arn
}

output "ddb_users_table" {
  description = "DynamoDB users table name"
  value       = module.dynamodb.users_table_name
}

output "ddb_courses_table" {
  description = "DynamoDB courses table name"
  value       = module.dynamodb.courses_table_name
}

output "ddb_study_events_table" {
  description = "DynamoDB study events table name"
  value       = module.dynamodb.study_events_table_name
}

output "opensearch_collection" {
  description = "OpenSearch Serverless collection name"
  value       = module.opensearch.collection_name
}
