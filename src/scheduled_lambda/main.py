import json
import traceback


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
