import json
import traceback
import os
import requests
import boto3

discord_api_base_url = "https://discord.com/api/v10"
bot_token = os.getenv("DISCORD_BOT_TOKEN")

daily_sports_channel_id_param_name = os.getenv('DAILY_SPORTS_POLL_PARAMETER_NAME')
ssm_client = boto3.client('ssm')


def lambda_handler(event, context):
    """
    The "scheduled" lambda: all scheduler actions trigger this lambda with different event types
    """
    event_type = 'unknown'
    try:
        payload = extract_event_payload(event)
        event_type = extract_event_type(payload)
        if event_type == 'test':
            print('Test event, ignoring...')
            return payload, event_type
        elif event_type == 'daily_sports_poll':
            print('Received event to post daily sports poll to Discord...')
            channel_id = get_daily_sports_poll_channel_id()
            send_daily_sports_poll_message(channel_id)
            print('Successfully posted daily sports poll.')
        else:
            print(f'Cannot handle event because event type is unknown: {event_type}')
    except BaseException as e:
        print(f'Failed to handle event with type {event_type} due to unexpected error. Event body follows:')
        print(json.dumps(event))
        traceback.print_exc()


def extract_event_payload(event: dict) -> dict:
    payload: str = event['Payload']  # payload comes from Terraform
    return json.loads(payload)


def extract_event_type(payload: dict) -> str:
    if 'event_type' in payload:
        return payload['event_type']
    else:
        print(f'Key "event_type" is not present in payload, cannot extract event type! Payload: {json.dumps(payload)}')


def get_daily_sports_poll_channel_id():
    ssm_parameter = ssm_client.get_parameter(Name=daily_sports_channel_id_param_name)
    return ssm_parameter['Parameter']['Value']


def send_daily_sports_poll_message(channel_id):
    response = requests.post(
        f'{discord_api_base_url}/channels/{channel_id}/messages',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bot {bot_token}'
        },
        json={
            'poll': build_daily_sports_poll_object()
        }
    )
    print(f'Discord API response to daily sports poll request: {response.json()}')
    response.raise_for_status()


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
                        'name': '💪'  # This is literally how discord API docs recommend it...
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
        'allow_multiselect': False,
    }
