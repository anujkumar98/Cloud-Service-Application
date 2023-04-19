output "application_security_group_id" {
  value = aws_security_group.application_security_group.id
}
output "database_security_group_id" {
  value = aws_security_group.database_security_group.id
}

output "load_balancer_security_group" {
  value = aws_security_group.load_balancer_security_group.id
}