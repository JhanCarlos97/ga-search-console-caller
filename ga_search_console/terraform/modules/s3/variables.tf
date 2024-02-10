variable "ENV" {}

variable "PROJECT_NAME" {}

variable "RESOURCE_SUFFIX" {}

variable "ENABLE_LIFECYCLE" {
  default = "Disabled"
}

variable "ENABLE_VERSIONING" {
  default = "Enabled"
}

variable "S3_NOTIFICATION_TOPIC_ARN" {
  default = ""
}

variable "S3_NOTIFICATION_FILTER_PREFIX" {
  default = "/"
}

variable "AWS_TAGS" { type=map(string) }