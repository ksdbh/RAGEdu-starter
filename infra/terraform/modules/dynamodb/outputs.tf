output "users_table_name" {
  value = aws_dynamodb_table.users.name
}

output "courses_table_name" {
  value = aws_dynamodb_table.courses.name
}

output "study_events_table_name" {
  value = aws_dynamodb_table.study_events.name
}
