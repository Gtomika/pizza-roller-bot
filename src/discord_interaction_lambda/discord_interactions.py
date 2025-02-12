import requests
import os
from typing import Union

discord_api_base_url = 'https://discord.com/api/v10'
discord_interaction_timeout = 5

# path variables: application ID, interaction token
edit_original_response_url = discord_api_base_url + '/webhooks/{application_id}/{interaction_token}/messages/@original'

application_id = os.getenv('APPLICATION_ID')
bot_token = os.getenv('BOT_TOKEN')


class WebhookPersonality:
    """
    Represents how the bot appears in webhook messages.
    """

    def __init__(self, bot_name: str, bot_icon_url: str):
        self.bot_name = bot_name
        self.bot_icon_url = bot_icon_url


class AllowedMention:
    """
    Class for the possible allowed mention types in a message.
    """

    def __init__(self, mention_type: str):
        self.mention_type = mention_type

    def mentions_allowed(self) -> bool:
        return self.mention_type != 'none'


allow_role_mentions = AllowedMention('roles')
allow_user_mentions = AllowedMention('users')
allow_everyone_mentions = AllowedMention('everyone')  # includes @here
allow_no_mentions = AllowedMention('none')


def respond_to_discord_interaction(
        interaction_token: str,
        message: str,
        allowed_mention: AllowedMention = allow_no_mentions,
        embeds: Union[list[dict], None] = None
):
    """
    Respond to a discord interaction, identified by the interaction token.
    Allowed mention should be used to control who this message can ping. By default
    it cannot ping anyone or any role.
    """
    url = edit_original_response_url.format(application_id=application_id, interaction_token=interaction_token)
    response = requests.patch(url, json={
        'content': message,
        'allowed_mentions': {
            'parse': [allowed_mention.mention_type] if allowed_mention.mentions_allowed() else []
        },
        'embeds': embeds if embeds is not None else []
    }, headers={
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }, timeout=discord_interaction_timeout)

    if response.status_code >= 400:
        print(f'Error while making edit to original interaction message, status: {response.status_code},'
              f' data: {response.content}')
        raise requests.exceptions.RequestException(f'Error {response.status_code}: {response.content}')


def create_webhook_message(
        webhook_url: str,
        message: str,
        personality: WebhookPersonality,
        allowed_mention: AllowedMention = allow_no_mentions
):
    """
    Create a new message on Discord using the given webhook.
    Allowed mention should be used to control who this message can ping. By default
    it cannot ping anyone or any role.
    """
    try:
        response = requests.post(url=f'{webhook_url}?wait=true', json={
            'content': message,
            'username': personality.bot_name,
            'avatar_url': personality.bot_icon_url,
            'allowed_mentions': {
                'parse': [allowed_mention.mention_type] if allowed_mention.mentions_allowed() else []
            }
        }, headers={
            'Content-Type': 'application/json'
        }, timeout=discord_interaction_timeout)

        if response.status_code >= 400:
            print(f"""Error response from Discord API while making webhook request
                - Status {response.status_code}
                - Response: {response.text}""")
    except requests.exceptions.RequestException as e:
        # because the webhook URL is not validated, anything must be expected from the user...
        # in case of invalid URL requests lib will throw this exception: don't want it to propagate
        print(f'Failed to send webhook to Discord. Webhook URL: {webhook_url}. Exception: {str(e)}')
