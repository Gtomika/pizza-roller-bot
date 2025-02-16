import boto3
import json
from datetime import datetime, timedelta

from src.commons import lambda_utils

aws_app_name = lambda_utils.get_env_var('APP_NAME')
aws_environment = lambda_utils.get_env_var('ENVIRONMENT')
aws_region = lambda_utils.get_env_var('AWS_REGION')

# ARN of the role that the scheduler is going to assume: this role is created by Terraform and has necessary permissions
scheduler_role_arn = lambda_utils.get_env_var('SCHEDULER_ROLE_ARN')

# scheduling group that this script is going to create new schedules in
scheduler_group_name = lambda_utils.get_env_var('SCHEDULER_GROUP_NAME')

# describes the action that the scheduler is going to trigger -> in this case, invoke a lambda function
scheduler_target_type_arn = 'arn:aws:scheduler:::aws-sdk:lambda:invoke'

scheduler_client = boto3.client('scheduler')


def schedule_trigger_of_lambda(
        lambda_arn: str,
        name_prefix: str,
        event_type: str,
        trigger_in_hours: int
):
    scheduler_client.create_schedule(
        Name=__create_schedule_name(name_prefix),
        GroupName=scheduler_group_name,
        ScheduleExpression=__create_fixed_time_schedule_expression(trigger_in_hours),
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },
        Target=__create_lambda_target(lambda_arn, event_type),
        ScheduleExpressionTimezone='Europe/Budapest',
        Description=f'Schedule that will trigger the lambda with ARN {lambda_arn} in {trigger_in_hours} hours. Name prefix: {name_prefix}',
        ActionAfterCompletion='DELETE'  # since this is a one time trigger
        # TODO: add tags to the schedule
    )


def __create_schedule_name(prefix: str) -> str:
    return f'{prefix}-{aws_app_name}-{aws_environment}-{aws_region}'


def __create_fixed_time_schedule_expression(trigger_in_hours: int) -> str:
    # needs to be in the format of 'at(yyyy-mm-ddThh:mm:ss)'
    trigger_time = (datetime.now() + timedelta(hours=trigger_in_hours)).strftime('%Y-%m-%dT%H:%M:%S')
    return f'at({trigger_time})'


def __create_lambda_target(lambda_arn: str, event_type: str) -> dict:
    return {
        'RoleArn': scheduler_role_arn,
        'Arn': scheduler_target_type_arn,
        'Input': json.dumps({
            'FunctionName': lambda_arn,
            'InvocationType': 'Event',
            'Payload': json.dumps({
                'event_type': event_type,
            })
        })
    }