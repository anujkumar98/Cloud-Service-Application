resource "random_uuid" "uuid" {}

resource "aws_s3_bucket" "s3_bucket_csye6225" {
  bucket        = "csye-6225-${random_uuid.uuid.result}-${var.aws_default_profile}"
  acl           = "private"
  force_destroy = true
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  lifecycle_rule {
    id      = "s3_bucket_csye6225_policy"
    enabled = true
    prefix  = ""
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}
resource "aws_s3_bucket_public_access_block" "public_access_block" {
  bucket                  = aws_s3_bucket.s3_bucket_csye6225.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

