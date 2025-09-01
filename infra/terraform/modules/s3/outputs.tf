output "bucket_name" {
  value = aws_s3_bucket.docs.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.docs.arn
}

output "bucket_domain_name" {
  value = aws_s3_bucket.docs.bucket_domain_name
}
