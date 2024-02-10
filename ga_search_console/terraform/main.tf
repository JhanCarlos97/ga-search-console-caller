data "aws_region" "current_region" {}

locals {
  PROJECT_NAME                 = "company-ga-search-console"
  ENV                          = terraform.workspace
  AWS_REGION                   = data.aws_region.current_region.name
  AWS_TAGS                     = var.AWS_TAGS
}

########################################################################################################################
# S3
########################################################################################################################

#S3 region
module "bucket-ga-search-console" {
  source          = "./modules/s3"
  ENV             = local.ENV
  PROJECT_NAME    = local.PROJECT_NAME
  RESOURCE_SUFFIX = "data"
  AWS_TAGS        = local.AWS_TAGS
}
#endregion

########################################################################################################################
# Secret manager
########################################################################################################################


#These resources are defined manually in each account
data "aws_secretsmanager_secret" "ga_credentials_secret" {
  name = "company/reporting/${local.ENV}/gasearchconsole/admin"
}

########################################################################################################################
# LAMBDAS
########################################################################################################################
#lambda region
module "lambda-ga-search-console" {
  source                          = "./modules/lambda"
  ENV                             = local.ENV
  PROJECT_NAME                    = local.PROJECT_NAME
  RESOURCE_SUFFIX                 = "caller"
  LAMBDA_LAYER                    = [module.lambda-layer.arn]
  LAMBDA_SETTINGS                 = {
    "description"                 = "This function retrieve the information from GA Search Console of company"
    "handler"                     = "ga-search-console-caller.lambda_handler"
    "runtime"                     = "python3.8"
    "timeout"                     = 600
    "memory_size"                 = 128
    "lambda_script_folder"        = "../lambdas/"
  }
  SECRET_MANAGERS_ARN             = [
      data.aws_secretsmanager_secret.ga_credentials_secret.arn
  ]
  BUCKET_ARN                      = module.bucket-ga-search-console.arn
  LAMBDA_ENVIRONMENT_VARIABLES    = {
    "SLACK_CHANNEL_WEBHOOK"       = "https://hooks.slack.com/services/rest_of_url_webhook"
    "BUCKET_NAME"                 = module.bucket-ga-search-console.id
    "SECRET_MANAGER_NAME"         = data.aws_secretsmanager_secret.ga_credentials_secret.name
    "ENV"                         = local.ENV
  }
  CREATE_INVOKER_TRIGGER          = true
  LAMBDA_EXECUTION_FREQUENCY      = {
    dev = {
      rate                       = "1440"
      unity                      = "minutes"
    }
    qa = {
      rate                       = "1440"
      unity                      = "minutes"
    }
    stg = {
      rate                       = "1440"
      unity                      = "minutes"
    }
    prd = {
      rate                       = "720"
      unity                      = "minutes"
    }
  }
  AWS_TAGS                        = local.AWS_TAGS
}

#region lambda-layer
module "lambda-layer" {
  source                = "./modules/lambda-layer"
  ENV                   = local.ENV
  PROJECT_NAME          = local.PROJECT_NAME
  RESOURCE_SUFFIX       = "lambda-layer"
  BUILDER_SCRIPT_PATH   = "../utils/lambda-layer-builder.sh"
  REQUIREMENTS_PATH     = "requirements.txt"
  PACKAGE_OUTPUT_NAME   = "lambda-layer"
}
#endregion
