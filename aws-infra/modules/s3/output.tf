output "aws_s3_id" {
  value = aws_s3_bucket.s3_bucket_csye6225.id
}
output "aws_s3_arn" {
  value = aws_s3_bucket.s3_bucket_csye6225.arn
}

output "aws_bucket_name" {
  value = aws_s3_bucket.s3_bucket_csye6225.bucket
}