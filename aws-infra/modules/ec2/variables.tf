variable "vpc_instance_id" {
  type        = string
  description = "ID for VPC"
}
variable "security_group_id" {
  type        = list(string)
  description = "ID for the security group"
}
variable "subnet_id" {
  type        = string
  description = "id for the subnet"
}
variable "instance_type" {
  type        = string
  description = "Type of instance"
  default     = "t2.micro"
}
variable "public_key_path" {
  description = "Public key path"
  default     = "~/.ssh/aws_ssh_key.pub"
}
variable "ami_id" {
  description = "Id for AMI"
}
variable "key_name" {
  description = "key name for ssh"
  type        = string
}
variable "access_policy_attachemet_name" {
  type = string
}
variable "rds_endpoint" {
  type = string
}

variable "rds_username" {
  type = string
}
variable "rds_password" {
  type = string
}
variable "s3_bucket_name" {
  type = string
}