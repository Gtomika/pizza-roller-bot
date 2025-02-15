import boto3
import random

from src.commons import discord_api
from src.commons import lambda_utils
from src.commons import discord_utils

daily_sports_channel_id_param_name = lambda_utils.get_env_var('DAILY_SPORTS_POLL_PARAMETER_NAME')
ssm_client = boto3.client('ssm')

# will be attached to the message as text, after '@everyone'
content_options = [
    f', szavazzatok különben Lili mérges lesz {discord_utils.default_emote("flushed")}',
    f', szavazzatok, hogy megtöltsük az Excel táblát {discord_utils.default_emote("notepad_spiral")}',
    f', szavazzatok különben kakkantók vagytok {discord_utils.default_emote("poop")}',
]


def get_daily_sports_poll_channel_id():
    ssm_parameter = ssm_client.get_parameter(Name=daily_sports_channel_id_param_name)
    return ssm_parameter['Parameter']['Value']
    # return '968777260712747029' # -> test channel on Nubaras test server


def send_daily_sports_poll_message(channel_id):
    poll_object = build_daily_sports_poll_object()
    message_body = discord_api.create_message_body(f'@everyone{random.choice(content_options)}', poll=poll_object)
    discord_api.post_message(channel_id, message_body)


def build_daily_sports_poll_object():
    return {
        'question': {
            'text': 'Sportoltál ma? Ha csak fogsz, az is számít.'
        },
        'answers': [
            {
                'answer_id': 1,
                'poll_media': {
                    'text': 'Igen!',
                    'emoji': {
                        'name': '💪'
                    }
                }
            },
            {
                'answer_id': 2,
                'poll_media': {
                    'text': 'Nem...',
                    'emoji': {
                        'name': '🙄'
                    }
                }
            }
        ],
        'duration': 6,
        'allow_multiselect': False
    }
