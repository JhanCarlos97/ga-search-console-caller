locals {
  RESOURCE_NAME = "${var.PROJECT_NAME}-${var.ENV}-${var.RESOURCE_SUFFIX}"
}

resource "aws_lambda_layer_version" "python-layer" {
  filename            =  "../utils/lambda-layer.zip"
  layer_name          = var.RESOURCE_SUFFIX
  compatible_runtimes = [var.PYTHON_RUNTIME]
  skip_destroy        = false
  description         = "Layer for GA4 "
}