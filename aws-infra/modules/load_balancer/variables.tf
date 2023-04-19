variable "security_group_id" {
  type = list(string)
}
variable "lb_subnets" {
  type = list(string)
}
variable "vpc_id" {
  type = string
}
variable "webapp_url" {
  type = string
}
