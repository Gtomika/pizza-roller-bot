import json
import traceback

import daily_sports_poll


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
            channel_id = daily_sports_poll.get_daily_sports_poll_channel_id()
            daily_sports_poll.send_daily_sports_poll_message(channel_id, context.invoked_function_arn)
            print('Successfully posted daily sports poll.')
        elif event_type == 'process_daily_sports_poll':
            print('Received event to process daily sports poll results...')
            daily_sports_poll.process_daily_sports_poll_results()
            print('Successfully processed daily sports poll results.')
        else:
            print(f'Cannot handle event because event type is unknown: {event_type}')
    except BaseException as e:
        print(f'Failed to handle event with type {event_type} due to unexpected error. Event body follows:')
        print(json.dumps(event))
        traceback.print_exc()


def extract_event_payload(event: dict) -> dict:
    payload: str = event['Payload']  # payload comes AWS EventBridge Scheduler
    return json.loads(payload)


def extract_event_type(payload: dict) -> str:
    if 'event_type' in payload:
        return payload['event_type']
    else:
        print(f'Key "event_type" is not present in payload, cannot extract event type! Payload: {json.dumps(payload)}')
