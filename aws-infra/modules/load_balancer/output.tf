output "load_balancer_public_ip" {
  value = aws_lb.webapp_application_lb.dns_name
}

output "lb_target_group_arn" {
  value = aws_lb_target_group.webapp_lb_target_group.arn
}

output "lb_zone_id" {
  value = aws_lb.webapp_application_lb.zone_id
}