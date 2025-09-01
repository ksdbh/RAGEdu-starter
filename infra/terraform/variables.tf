variable "region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "ragedu"
}

variable "bucket_name" {
  type    = string
  default = "ragedu-docs-example"
}

# If empty, a default of "${project}-vec" will be used (see main.tf locals)
variable "opensearch_collection_name" {
  type    = string
  default = ""
}

# Optional tags map applied to the S3 bucket (and available for future resources)
variable "tags" {
  type    = map(string)
  default = {}
}
