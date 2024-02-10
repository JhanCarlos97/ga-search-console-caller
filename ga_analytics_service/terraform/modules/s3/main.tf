locals {
  BUCKET_NAME = "${var.PROJECT_NAME}-${var.ENV}-${var.RESOURCE_SUFFIX}"
}

#### Bucket S3 ####

resource "aws_s3_bucket" "bucket" {
  bucket = local.BUCKET_NAME
  tags = var.AWS_TAGS
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_sse" {
  bucket = aws_s3_bucket.bucket.id
  rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "bucket_lifecicyle_configuration" {
  bucket = aws_s3_bucket.bucket.id

  rule {
    id     = "expires_versioned_objects"
    status = var.ENABLE_LIFECYCLE

    expiration {
      expired_object_delete_marker = true
    }
    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.bucket.id
  versioning_configuration {
    status = var.ENABLE_VERSIONING
  }
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  count  = var.S3_NOTIFICATION_TOPIC_ARN == "" ? 0 : 1

  bucket = aws_s3_bucket.bucket.id
  topic {
    topic_arn     = var.S3_NOTIFICATION_TOPIC_ARN
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = var.S3_NOTIFICATION_FILTER_PREFIX
  }
}