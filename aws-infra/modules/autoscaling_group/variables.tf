variable "ami_id" {
  description = "Id for AMI"
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
# variable "key_name" {
#   description = "key name for ssh"
#   type        = string
# }
variable "access_policy_attachemet_name" {
  type = string
}
variable "security_group_id" {
  type        = list(string)
  description = "ID for the security group"
}
variable "cooldown_period" {
  type    = number
  default = 60
}
variable "lb_target_group_arn" {
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
variable "subnet_id" {
  type        = list(string)
  description = "id for the subnet"
}