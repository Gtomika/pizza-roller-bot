from src.discord_interaction_lambda import main


def local_lambda():
    # lambda event and context are not used yet
    main.lambda_handler(None, None)


if __name__ == '__main__':
    local_lambda()