variable "vpc_instance_id" {
  type        = string
  description = "ID for VPC"
}

variable "vpc_cidr_value" {
  type        = string
  description = "Cidr for main vpc"
  default     = "10.0.0.0/16"
}
