resource "aws_autoscaling_group" "webapp_autoscaling_group" {
  name                = "csye6225-asg-spring2023"
  max_size            = 3
  min_size            = 1
  desired_capacity    = 1
  health_check_type   = "EC2"
  default_cooldown    = var.cooldown_period
  vpc_zone_identifier = var.subnet_id
  tag {
    key                 = "webapp"
    value               = "webappInstance"
    propagate_at_launch = true
  }
  launch_template {
    id      = aws_launch_template.asg_launch_template.id
    version = "$Latest"
  }
  target_group_arns = [
    var.lb_target_group_arn
  ]
}

resource "random_uuid" "uuid" {}

resource "aws_key_pair" "ec2key" {
  key_name   = "ssh_key-${random_uuid.uuid.result}"
  public_key = file(var.public_key_path)
}

data "template_file" "user_data" {
  template = <<EOF
#!/bin/bash
cd /tmp/webapp
touch .env
sudo chown ec2-user:ec2-user .env
{
  echo "HOST=${var.rds_endpoint}"
  echo "USERNAME=${var.rds_username}" 
  echo "PASSWORD=${var.rds_password}"
  echo "SCHEMA_NAME=csye6225"
  echo "S3_Bucket_Name=${var.s3_bucket_name}"
} >> .env
  sudo systemctl daemon-reload
  sudo systemctl enable fastapi_service
  sudo systemctl start fastapi_service
 EOF
}

resource "aws_launch_template" "asg_launch_template" {
  name = "asg_launch_template"
  image_id      = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.ec2key.key_name
  iam_instance_profile {
    name = var.access_policy_attachemet_name
  }
  user_data = base64encode(data.template_file.user_data.rendered)
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 50
      volume_type           = "gp2"
      delete_on_termination = true
      encrypted             = true
      kms_key_id            = aws_kms_key.ebs_encrypt_key.arn
    }
  }
  network_interfaces {
    associate_public_ip_address = true
    security_groups             = var.security_group_id
    subnet_id                   = element(var.subnet_id, 1)
  }
}

resource "aws_autoscaling_policy" "scale_up_policy" {
  name                   = "scale-up-policy"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 60
  autoscaling_group_name = aws_autoscaling_group.webapp_autoscaling_group.name
}

resource "aws_cloudwatch_metric_alarm" "scale_up_alarm" {
  alarm_name                = "scale-up-alarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/EC2"
  statistic                 = "Average"
  threshold                 = "47"
  period                    = "60"
  alarm_description         = "Scale up when average CPU usage is greater than 47%"
  alarm_actions             = ["${aws_autoscaling_policy.scale_up_policy.arn}"]
  insufficient_data_actions = []
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.webapp_autoscaling_group.name
  }

}

resource "aws_autoscaling_policy" "scale_down_policy" {
  name                   = "scale-down-policy"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 60
  autoscaling_group_name = aws_autoscaling_group.webapp_autoscaling_group.name
}
resource "aws_cloudwatch_metric_alarm" "scale_down_alarm" {
  alarm_name          = "scale-down-alarm"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "44"
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.webapp_autoscaling_group.name
  }
  alarm_description         = "Scale down when average CPU usage is below 44%"
  alarm_actions             = ["${aws_autoscaling_policy.scale_down_policy.arn}"]
  insufficient_data_actions = []
}

resource "aws_autoscaling_attachment" "asg_lb_attachment" {
  autoscaling_group_name = aws_autoscaling_group.webapp_autoscaling_group.name
  lb_target_group_arn    = var.lb_target_group_arn
}
data "aws_caller_identity" "current" {}

resource "aws_kms_key" "ebs_encrypt_key" {
  description         = "My customer managed key"
  enable_key_rotation = true
  deletion_window_in_days = 10
  policy = jsonencode({
    "Id": "key-consolepolicy-3",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
            },
            "Action":"kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow use of the key",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
                    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
                ]
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow attachment of persistent resources",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
                    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling"
                ]
            },
            "Action": [
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "kms:GrantIsForAWSResource": "true"
                }
            }
        }
    ]
})
  tags = {
    "Name" = "ec2-key"
  }
}
