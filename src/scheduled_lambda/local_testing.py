import main
import json

if __name__ == '__main__':
    event = {
        'Payload': json.dumps({
            'event_type': 'daily_sports_poll'
        })
    }
    main.lambda_handler(event, None)
