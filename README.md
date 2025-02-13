# Pizza Roller Discord Bot

Top secret Discord bot for a top secret group.

## What this bot can do

This bot is equipped to support slash `/` commands, but right now no slash commands 
are added.

Additionally, the bot is able to create a daily sports poll to a preselected channel. This 
channel is configurable from AWS SSM parameter store.

## How to develop

The bot is written in Python 3.12. Install required dependencies by:

```bash
python -m pip install -r requirements-local.txt
```

## How to deploy

I was too lazy to write a Ci/Cd pipeline for this project, so deployment is documented here.
Requires that Python 3 and Terraform is installed.

Create required ZIP files in the `artifacts` folder:

```bash
python build_lambda_artifacts.py
```

Initialize Terraform (set variables seen in the command):

```bash
terraform init -backend-config="bucket=${TERRAFORM_STATE_BUCKET}" -backend-config="key=${TERRAFORM_STATE_FILE}" -backend-config="region=${AWS_REGION}"
```

The file `secrets.auto.tfvars` with sensitive variables is not checked into git. Only I have it.

Plan infrastructure changes:

```bash
terraform plan -out bot.tfplan
```

Apply infrastructure changes, using the plan created above. It might take some time to run.

```bash
terraform apply bot.tfplan
```

If all commands are successful, the bot is live on AWS.

## Tear down

This removes all traces of the bot infrastructure from existence.

```bash
terraform destroy
```

Note that the actual Discord application is not deleted, only the AWS resources.