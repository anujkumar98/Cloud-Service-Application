variable "vpc_instance_id" {
  type        = string
  description = "ID for VPC"
}

variable "igw_id" {
  type        = string
  description = "ID for IGW"
}

variable "public_subnet_id" {
  type        = list(any)
  description = "List of public subnet id"
}

variable "private_subnet_id" {
  type        = list(any)
  description = "List of private subnet id"
}
