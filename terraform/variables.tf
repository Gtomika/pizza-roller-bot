variable "app_name" {
  type = string
  description = "A name for the bot to be used in resource naming"
}

variable "aws_region" {
  type = string
  description = "Deployment AWS region"
}

variable "environment" {
  type = string
  description = "Deployment environment for example 'prd'"
}

variable "discord_bot_token" {
  type = string
  sensitive = true
  description = "The Bot token that authorizes the bot to communicate with the Discord API"
}

variable "aws_key_id" {
  type = string
  sensitive = true
  description = "AWS access key ID"
}

variable "aws_secret_key" {
  type = string
  sensitive = true
  description = "AWS secret key"
}

variable "aws_terraform_role_arn" {
  type = string
  description = "ARN of the role Terraform must assume"
}

variable "aws_assume_role_external_id" {
  type = string
  sensitive = true
  description = "Secret required to assume the Terraform role"
}

variable "discord_application_id" {
  type = number
  description = "Number that is the ID of the Discord bot"
}

variable "discord_application_public_key" {
  type = string
  description = "Public key for the bot"
}

variable "discord_application_name" {
  type = string
  description = "The Bots name as it appears in Discord"
}

variable "developer_email_address" {
  type = string
  description = "Email of developer that is subscribed to SNS topics such as error topic"
}

variable "oauth_client_id" {
  type = string
  description = "Discord app's oauth client id"
}

variable "oauth_client_secret" {
  type = string
  description = "Discord app's oauth client secret"
}

variable "daily_sports_poll_channel_id" {
  type = string
  description = "Discord channel ID for daily sports poll"
}
