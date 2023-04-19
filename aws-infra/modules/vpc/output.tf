output "vpc_instance_id" {
  description = "ID of the vpc"
  value       = aws_vpc.vpc.id
}

output "internet_gateway_id" {
  value = aws_internet_gateway.igw.id
}