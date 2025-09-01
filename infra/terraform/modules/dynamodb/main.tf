resource "aws_dynamodb_table" "users" {
  name         = "${var.project}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  // Consider adding TTL, streams, and additional GSIs in production
}

resource "aws_dynamodb_table" "courses" {
  name         = "${var.project}-courses"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "course_id"

  attribute {
    name = "course_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "study_events" {
  name         = "${var.project}-study-events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  // Example usage: pk = "user#<id>", sk = "event#<timestamp>" or similar
}
