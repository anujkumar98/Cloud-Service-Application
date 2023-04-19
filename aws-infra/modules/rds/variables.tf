variable "private_subnet_id" {
  type = list(string)
}
variable "security_group_id" {
  type = string
}

variable "private_subnet_name" {
  type = list(string)
}

variable "uuid_generated" {
  type = string
}
variable "rds_username" {
  type = string
}
variable "rds_password" {
  type = string
}