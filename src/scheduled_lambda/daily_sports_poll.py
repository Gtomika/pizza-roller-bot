import boto3
import random

from src.commons import discord_api
from src.commons import lambda_utils
from src.commons import pizza_roll_internal

import scheduling_utils

daily_sports_poll_duration_hours = 8
daily_sports_channel_id_param_name = lambda_utils.get_env_var('DAILY_SPORTS_POLL_CHANNEL_ID_PARAMETER_NAME')
daily_sports_message_id_param_name = lambda_utils.get_env_var('DAILY_SPORTS_POLL_MESSAGE_ID_PARAMETER_NAME')
ssm_client = boto3.client('ssm')

sports_poll_yes_answer_id = 1
sports_poll_no_answer_id = 2


def send_daily_sports_poll_message(lambda_arn):
    poll_object = __build_daily_sports_poll_object()
    voting_encouragement = f'@everyone {random.choice(pizza_roll_internal.daily_sports_poll_voting_encouragements)}'
    message_body = discord_api.create_message_body(content=voting_encouragement, poll=poll_object)
    channel_id = __get_daily_sports_poll_channel_id()
    message_created_response = discord_api.post_message(channel_id, message_body)
    message_id = message_created_response['id']
    print(f'Daily sports poll message created with id: {message_id}')
    __save_daily_sports_poll_message_id(message_id)
    # --- disabled until bot has necessary permissions to process the results ---
    # __create_daily_sports_poll_result_processor(lambda_arn)


def process_daily_sports_poll_results():
    channel_id = __get_daily_sports_poll_channel_id()
    message_id = __get_daily_sports_poll_message_id()
    message_body = discord_api.create_message_body(
        content=random.choice(pizza_roll_internal.daily_sports_poll_results_processing_messages),
        poll=None,
        reply_to_message_with_id=message_id
    )
    discord_api.post_message(channel_id, message_body)
    print(f'Successfully sent reply message to the daily sports poll (original message id: {message_id}).')
    # TODO implement saving the results


def __get_daily_sports_poll_channel_id():
    ssm_parameter = ssm_client.get_parameter(Name=daily_sports_channel_id_param_name)
    return ssm_parameter['Parameter']['Value']
    # return '968777260712747029' # -> test channel on Nubaras test server


def __build_daily_sports_poll_object():
    return {
        'question': {
            'text': 'Sportoltál ma? Ha csak fogsz, az is számít.'
        },
        'answers': [
            {
                'answer_id': sports_poll_yes_answer_id,
                'poll_media': {
                    'text': 'Igen!',
                    'emoji': {
                        'name': '💪'
                    }
                }
            },
            {
                'answer_id': sports_poll_no_answer_id,
                'poll_media': {
                    'text': 'Nem...',
                    'emoji': {
                        'name': '🙄'
                    }
                }
            }
        ],
        'duration': daily_sports_poll_duration_hours,
        'allow_multiselect': False
    }


def __save_daily_sports_poll_message_id(message_id):
    ssm_client.put_parameter(Name=daily_sports_message_id_param_name, Value=message_id, Overwrite=True)
    print(f'Updated daily sports poll message id in SSM parameter store to value: {message_id}')


def __get_daily_sports_poll_message_id():
    ssm_parameter = ssm_client.get_parameter(Name=daily_sports_message_id_param_name)
    return ssm_parameter['Parameter']['Value']


def __create_daily_sports_poll_result_processor(lambda_arn):
    name_prefix = 'DailySportsPollResultProcessor'
    scheduling_utils.schedule_trigger_of_lambda(
        lambda_arn=lambda_arn,
        name_prefix=name_prefix,
        event_type='process_daily_sports_poll',
        trigger_in_hours=daily_sports_poll_duration_hours+1
    )
    print(f'Scheduled the {name_prefix} to trigger in {daily_sports_poll_duration_hours+1} hours')
