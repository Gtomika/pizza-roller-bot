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
Requires that Python 3, Docker and Terraform is installed.

Create required ZIP files in the `artifacts` folder. This should be done on a Amazon Lambda runtime Python 3.12 Linux environment, 
as the created libraries in the ZIP files will be executed in such environment.

First, create docker container of Amazon Lambda Python 3.12 runtime, and copy the necessary files in. Inside this projects 
root folder, execute:

```bash
docker pull public.ecr.aws/lambda/python:3.12
docker run --name amzn -d -t --rm public.ecr.aws/lambda/python:3.12 /bin/bash
docker cp requirements-lambda.txt amzn:/root/requirements-lambda.txt
docker cp build_lambda_artifacts.py amzn:/root/build_lambda_artifacts.py
docker cp src amzn:/root/src
```

Then log into this docker container:

```bash
docker exec -it amzn bash
```

Inside the container, build the lambda artifacts:

```bash
cd /root
export SKIP_LAYER_BUILDING=0
python build_lambda_artifacts.py
exit
```

Then copy the artifacts out:

```bash
mkdir artifacts
docker cp amzn:/root/artifacts .
```

Now the `artifacts` folder with the ZIP files is present on your host OS and you can start deploying.

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

If all commands are successful, the bot is live on AWS. I really should automate this...

## Tear down

This removes all traces of the bot infrastructure from existence.

```bash
terraform destroy
```

Note that the actual Discord application is not deleted, only the AWS resources.