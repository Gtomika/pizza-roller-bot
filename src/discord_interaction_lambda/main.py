import os
import requests
import json

import discord_interactions
import api_gateway_interactions as agi
from nacl.signing import VerifyKey

ACK_TYPE = 1
RESPONSE_TYPE = 4
DEFER_TYPE = 5

discord_api_base_url = "https://discord.com/api/v10"
bot_token = os.getenv("DISCORD_BOT_TOKEN")

# Request verification
application_public_key = os.getenv('APPLICATION_PUBLIC_KEY')
verify_key = VerifyKey(bytes.fromhex(application_public_key))
signature_header_name = 'x-signature-ed25519'
timestamp_header_name = 'x-signature-timestamp'


# this lambda handler receives interaction events from Discord, through the AWS API Gateway
def lambda_handler(event, context):
    """
    Lambdalith for the Pizza Roller application. Handles request from API gateway, including discord interactions.
    :param event:
    :param context:
    :return:
    """
    # print(json.dumps(event, indent=4))
    headers, body_raw = agi.parse_api_gateway_event(event)
    body = json.loads(body_raw)

    # Required by Discord to perform check to validate that this call came from them
    if not is_request_verified(headers, body_raw):
        return agi.to_api_gateway_raw_response(401, 'invalid request signature')

    # ACK message that is required for Discord interaction URL
    if body['type'] == ACK_TYPE:
        return agi.to_api_gateway_response(200, {
            'type': ACK_TYPE
        })

    # process message (async) TODO
    return agi.to_api_gateway_response(200, {'message': 'ok'})


def is_request_verified(headers, body_raw: str) -> bool:
    if signature_header_name in headers and timestamp_header_name in headers:
        signature = headers[signature_header_name]
        timestamp = headers[timestamp_header_name]
    else:
        print(f'Either {signature_header_name} or {timestamp_header_name} header '
              f'was not found in the request: both are required')
        return False

    try:
        verify_key.verify(f'{timestamp}{body_raw}'.encode(), bytes.fromhex(signature))
        return True
    except Exception as e:  # any exception results in false
        print(f'Exception while validating request: {str(e)}')
        return False


def send_text_message(channel_id, content, access_token):
    request = requests.post(
        f'{discord_api_base_url}/channels/{channel_id}/messages',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bot {access_token}'
        },
        data={
            'content': content
        }
    )
    request.raise_for_status()
    print(f'Text message response: {request.json()}')
