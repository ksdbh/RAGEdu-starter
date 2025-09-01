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

resource "aws_s3_bucket" "docs" {
  bucket = var.bucket_name
}

resource "aws_dynamodb_table" "study" {
  name         = "${var.project}-study"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  attribute { name = "pk"; type = "S" }
}

# Placeholder: OpenSearch Serverless collection (vector-ready)
resource "aws_opensearchserverless_collection" "vec" {
  name = "${var.project}-vec"
  type = "SEARCH"
}

output "bucket" { value = aws_s3_bucket.docs.bucket }
output "ddb"    { value = aws_dynamodb_table.study.name }
output "oss"    { value = aws_opensearchserverless_collection.vec.name }
