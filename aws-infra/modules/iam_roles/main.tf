resource "aws_iam_policy" "webapp_s3" {
  name        = "webapp_s3_policy"
  description = "Allows EC2 instances to perform S3 operations on the WebAppS3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:Get*",
          "s3:Put*",
          "s3:Delete*"
        ]
        Resource : [
          var.s3_arn,
          "${var.s3_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "webapp_s3_role" {
  name = "EC2-CSYE6225"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "webapp_s3_instance_profile" {
  name = "EC2-CSYE6225_profile"

  role = aws_iam_role.webapp_s3_role.name
}
resource "aws_iam_role_policy_attachment" "webapp_s3_policy_attachment" {
  policy_arn = aws_iam_policy.webapp_s3.arn
  role       = aws_iam_role.webapp_s3_role.name
}

data "aws_iam_policy" "Cloudwatch_policy" {
  arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}
resource "aws_iam_role_policy_attachment" "webapp_cloudwatch_policy_attachment" {
  policy_arn = data.aws_iam_policy.Cloudwatch_policy.arn
  role       = aws_iam_role.webapp_s3_role.name
}
