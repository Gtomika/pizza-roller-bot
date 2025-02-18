import requests
from typing import Union

from src.commons import lambda_utils

discord_api_base_url = 'https://discord.com/api/v10'
discord_interaction_timeout = 5


application_id = lambda_utils.get_env_var('DISCORD_APPLICATION_ID')
bot_token = lambda_utils.get_env_var('DISCORD_BOT_TOKEN')


def __common_headers():
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bot {bot_token}'
    }


def create_message_body(
        content: str,
        poll: Union[dict, None] = None,
        reply_to_message_with_id: Union[str, None] = None
):
    """
    Creates a message body for a Discord message.
    :param content: The content of the message
    :param poll: Poll object to include in the message
    :param reply_to_message_with_id: ID of the message to reply to, optional
    :return: The body for further use with 'post_message' function
    """
    message_body = {
        'allowed_mentions': {
            'parse': ['everyone']
        },
        'content': content
    }
    if poll is not None:
        message_body['poll'] = poll
    if reply_to_message_with_id is not None:
        message_body['message_reference'] = {
            'message_id': reply_to_message_with_id
        }
    return message_body


def post_message(channel_id: str, message_body: dict):
    """
    Posts a message to a Discord channel.
    :param channel_id: The ID of the channel to post the message to
    :param message_body: Message specification according to Discord API, use 'create_message_body' to create it.
    :return: Response from the Discord API
    :except requests.HTTPError: If the request was not successful
    """
    response = requests.post(
        url=f'{discord_api_base_url}/channels/{channel_id}/messages',
        headers=__common_headers(),
        json=message_body
    )
    print(f'Discord API response to message post request: {response.json()}')
    response.raise_for_status()
    return response.json()


def get_poll_answers(channel_id: str, message_id: str, answer_id: int):
    response = requests.post(
        url=f'{discord_api_base_url}/channels/{channel_id}/messages/{message_id}/answers/{answer_id}',
        headers=__common_headers()
    )
