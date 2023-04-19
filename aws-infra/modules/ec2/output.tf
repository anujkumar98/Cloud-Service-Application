output "ec2_ip_addess" {
  value = aws_instance.aws_ec2_csye6225.public_ip
}