data "aws_route53_zone" "hosted_zone" {
  name = var.webapp_url
}
resource "aws_route53_record" "route53_record_csye6225" {
  zone_id = data.aws_route53_zone.hosted_zone.id
  name    = ""
  type    = "A"
  alias {
    name                   = var.lb_dns
    zone_id                = var.lb_zone_id
    evaluate_target_health = true
  }
}
