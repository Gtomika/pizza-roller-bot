# --------------------------------- IAM -------------------------------------------

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    sid = "AllowLambdaToAssume"
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data aws_iam_policy_document "lambda_policy" {
  statement {
    sid     = "AllowLambdaToLog"
    effect  = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.app_name}-LambdaRole-${var.environment}-${var.aws_region}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
  inline_policy {
    name = "${var.app_name}-LambdaPolicy-${var.environment}-${var.aws_region}"
    policy = data.aws_iam_policy_document.lambda_policy.json
  }
}

# --------------------------------- Lambdas -----------------------------------------

resource "aws_lambda_function" "discord_interaction_lambda" {
  function_name = "DiscordInteraction-${var.app_name}-${var.environment}-${var.aws_region}"
  role          = aws_iam_role.lambda_role.arn
  description = "Lambda monolith to perform Pizza Roller operations"

  # deployment package required to be already present when this runs
  filename = "../artifacts/discord_interaction_lambda.zip"
  source_code_hash = filebase64sha256("../artifacts/discord_interaction_lambda.zip")

  runtime = "python3.12"
  handler = "main.lambda_handler"
  memory_size = 512
  timeout = 30
  environment {
    variables = {
      DISCORD_BOT_TOKEN = var.discord_bot_token
      APPLICATION_PUBLIC_KEY = var.discord_application_public_key
    }
  }
}

resource "aws_lambda_function" "scheduled_lambda" {
  function_name = "Scheduled-${var.app_name}-${var.environment}-${var.aws_region}"
  role          = aws_iam_role.lambda_role.arn
  description = "Lambda triggered by AWS scheduler to perform tasks on time"

  # deployment package required to be already present when this runs
  filename = "../artifacts/scheduled_lambda.zip"
  source_code_hash = filebase64sha256("../artifacts/scheduled_lambda.zip")

  runtime = "python3.12"
  handler = "main.lambda_handler"
  memory_size = 512
  timeout = 30
  environment {
    variables = {

    }
  }
}

# -------------------------------- API gateway -------------------------------------

locals {
  api_gateway_name = "API-${var.app_name}-${var.environment}-${var.aws_region}"
}

# Configure access logging for the API gateway
resource "aws_cloudwatch_log_group" "api_gateway_log_group" {
  name = "/aws/apigateway/${local.api_gateway_name}"
  retention_in_days = 30
}

# Configure the API gateway
resource "aws_apigatewayv2_api" "api_gateway" {
  name          = local.api_gateway_name
  protocol_type = "HTTP"
  description = "API Gateway for ${var.app_name} application"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.api_gateway.id
  integration_type = "AWS_PROXY"
  description = "Forward to POST request to the ${aws_lambda_function.discord_interaction_lambda.function_name}"

  integration_method = "POST"
  integration_uri    = aws_lambda_function.discord_interaction_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.api_gateway.id
  route_key = "POST /pizza-roller"
  target = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "api_gateway_stage" {
  name          = "$default"
  api_id        = aws_apigatewayv2_api.api_gateway.id
  auto_deploy = true
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_log_group.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_deployment" "api_gateway_deployment" {
  api_id        = aws_apigatewayv2_api.api_gateway.id
  description = "Deployment for the ${local.api_gateway_name} HTTP API Gateway"

  # To avoid attempting deployment before route + integration are ready
  depends_on = [
    aws_apigatewayv2_integration.lambda_integration,
    aws_apigatewayv2_route.lambda_route,
  ]

  lifecycle { # to avoid downtime
    create_before_destroy = true
  }

  triggers = { # to avoid unnecessary re-deployments
    redeployment = sha1(join(",", tolist([
      jsondecode(aws_apigatewayv2_integration.lambda_integration),
      jsondecode(aws_apigatewayv2_route.lambda_route)
    ])))
  }
}

# Give permissions to API gateway to invoke lambdas
resource "aws_lambda_permission" "api_gateway_lambda_permission" {
  statement_id = "AllowAPIGatewayToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_interaction_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_apigatewayv2_api.api_gateway.execution_arn}/*"
}

# -------------------------------------------- scheduler ---------------------------------

locals {
  scheduler_name_suffix = "${var.app_name}-${var.environment}-${var.aws_region}"
}

resource "aws_scheduler_schedule_group" "schedule_group" {
  name = "Schedules-${local.scheduler_name_suffix}"
}

data "aws_iam_policy_document" "scheduler_policy" {
  statement {
    sid = "AllowToInvokeScheduledLambda"
    effect = "Allow"
    actions = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.scheduled_lambda.arn]
  }
}

data "aws_iam_policy_document" "scheduler_assume_policy" {
  statement {
    sid = "AllowToBeAssumedByScheduler"
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler_role" {
  name = "Scheduler-${local.scheduler_name_suffix}"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_policy.json
  inline_policy {
    name = "AllowSchedulerToInvokeLambda"
    policy = data.aws_iam_policy_document.scheduler_policy.json
  }
}

resource "aws_scheduler_schedule" "daily_sport_poll_schedule" {
  name = "DailySportPollSchedule-${local.scheduler_name_suffix}"
  group_name = aws_scheduler_schedule_group.schedule_group.id
  description = "Scheduled daily sport poll on Discord."

  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression = "cron(0 20 * * *)"
  schedule_expression_timezone = "Europe/Budapest"

  target {
    arn = aws_lambda_function.scheduled_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
    input = jsonencode({
      FunctionName = aws_lambda_function.scheduled_lambda.arn
      InvocationType = "Event"
      Payload = "{\"event_type\":\"daily_sports_poll\"}"
    })
  }
}