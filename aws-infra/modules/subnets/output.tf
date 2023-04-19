output "public_subnet_id" {
  description = "Id of the public subnet"
  value       = aws_subnet.public_subnet[*].id
}

output "private_subnet_id" {
  description = "Id of the private subnet"
  value       = aws_subnet.private_subnet[*].id
}

output "private_subnet_name" {
  description = "Name of the private subnets"
  value       = aws_subnet.private_subnet[*].tags.Name
}