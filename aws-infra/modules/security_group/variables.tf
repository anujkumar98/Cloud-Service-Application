variable "cidr_block" {
  type        = list(string)
  description = "Cidr for main vpc"
  default     = ["0.0.0.0/0"]
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

