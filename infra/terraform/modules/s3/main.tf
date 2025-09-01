resource "aws_s3_bucket" "docs" {
  bucket = var.bucket_name

  tags = merge({
    "Project" = var.project
  }, var.tags)

  // Note: consider adding ACL, lifecycle rules, encryption, and block_public_access for production
}
