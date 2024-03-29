variable "PROJECT_NAME" {}
variable "ENV" {}
variable "RESOURCE_SUFFIX" {}

variable "LAMBDA_LAYER" {
  type    = list(string)
  default = []
}

variable "LAMBDA_SETTINGS" {
  type = any
}

variable "LAMBDA_EVENT_SOURCE" {
  type = any
  default = {
    "event_source_arn"                    = ""
    "trigger"                             = ""
    "starting_position"                   = "LATEST"
    "batch_size"                          = 1
    "maximum_batching_window_in_seconds"  = 30
    "maximum_retry_attempts"              = 10
  }
}

variable LAMBDA_ENVIRONMENT_VARIABLES {
  type = map(string)
}

variable "LAMBDA_INVOKE_FUNCTION" {
  type = any
  default = {
    "type_arn"   = ""
    "target_arn" = ""
  }
}

variable "AWS_TAGS" { type=map(string) }

variable "SNS_TRIGGER_ARN" {
  type    = string
  default = ""
}

variable "ALARM_ARN" {
  default = ""
}

variable "ALARM_PERIOD" {
  type    = string
  default = "600"
}

variable "CREATE_INVOKER_TRIGGER" {
  type    = bool
  default = false
}

variable "INVOKER_TRIGGER_PARAMETERS" {
  type    = any
  default = {
    statement_id  = ""
    principal     = ""
    source_arn    = ""
  }
}

variable "VPC_SETTINGS" {
  type = any
  default = {
    "vpc_subnets"        = []
    "security_group_ids" = []
  }
}


variable "LAMBDA_EXECUTION_FREQUENCY" {
  type =  map(map(string))
  default = {
    dev = {
      rate  = "60"
      unity = "minutes"
    }
    qa = {
      rate  = "60"
      unity = "minutes"
    }
    stg = {
      rate  = "5"
      unity = "minutes"
    }
    prd = {
      rate  = "5"
      unity = "minutes"
    }
  }
}

variable "LOG_RETENTION_IN_DAYS" {
  type    =  number
  default =  14
}

variable "SECRET_MANAGERS_ARN" {
  type    = list(string)
  default = []
}

variable "BUCKET_ARN" {
  type    = string
  default = ""
}
