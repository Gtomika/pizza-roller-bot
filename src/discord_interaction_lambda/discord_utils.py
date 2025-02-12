import pendulum

from bot.commons import common_exceptions

ACK_TYPE = 1
RESPONSE_TYPE = 4
DEFER_TYPE = 5

loading_emote_id = 1095760395198808214
gem_emote_id = 1095760385149243443
commander_emote_id = 1095760375393308723
reward_potion_emote_id = 1095760398902362256
gold_emote_id = 1095767249475866765
wvw_icon_id = 1096784371488399420
legendary_armor_id = 1097446125230891078
github_emote_id = 1098604395836477480
astral_acclaim_emote_id = 1215267076906942464

developer_id = "416289572289249280"

admin_permission = 0x0000000000000008


class InteractionInfo:
    def __init__(self, event):
        self.user_id = extract_user_id(event)
        self.username = extract_username(event)
        self.locale = extract_locale(event)
        self.interaction_token = extract_interaction_token(event)
        if is_from_guild(event):
            self.guild_id = extract_guild_id(event)

# ------- data extraction ------------


def extract_guild_id(event):
    """
    Only call if event is guaranteed to be from guild
    """
    return event['guild_id']


def extract_info(event) -> InteractionInfo:
    return InteractionInfo(event)


def extract_locale(event) -> str:
    locale: str = event['locale']
    if locale.startswith('en'):
        locale = 'en'  # to avoid all this bullshit with 'en-UK' or 'en-US'
    return locale


def extract_username(event) -> str:
    if is_from_guild(event):
        return event['member']['user']['username']
    else:
        return event['user']['username']


def extract_user_id(event) -> int:
    if is_from_guild(event):
        return event['member']['user']['id']
    else:
        return event['user']['id']


def extract_interaction_token(event) -> str:
    return event['token']


def extract_option(event, option_name: str):
    """
    Get one option from the interaction event. Throws:
     - OptionNotFoundException
    """
    if 'options' not in event['data']:
        raise common_exceptions.OptionNotFoundException
    options = event['data']['options']

    for option in options:
        if option['name'] == option_name:
            return option['value']
    raise common_exceptions.OptionNotFoundException


def extract_subcommand_option(subcommand, option_name: str):
    """
    Extract an option from the subcommand object. Throws:
     - OptionNotFoundException
    """
    for option in subcommand['options']:
        if option['name'] == option_name:
            return option['value']
    raise common_exceptions.OptionNotFoundException


def extract_subcommand(event):
    """
    Call this when the command has subcommands, and would like to
    find out which subcommand was invoked.

    In this case 'options' is always provided with exactly one "option": the subcommand
    """
    return event['data']['options'][0]


def extract_member_roles(event):
    if not is_from_guild(event):
        return []
    return event['member']['roles']


# ------- event conditions ------------


def is_from_guild(event) -> bool:
    return 'member' in event


def is_admin(event) -> bool:
    if is_from_guild(event):
        permissions = int(event['member']['permissions'])
        return permissions & admin_permission == admin_permission
    else:
        return False

# ------- message formatting ------------


def custom_emote(name: str, emote_id: int) -> str:
    return f'<:{name}:{str(emote_id)}>'


def default_emote(name: str) -> str:
    return f':{name}:'


def animated_emote(name: str, emote_id: int) -> str:
    return f'<a:{name}:{str(emote_id)}>'


def mention_user(user_id: str) -> str:
    return f'<@{user_id}>'


def mention_role(role_id: str) -> str:
    return f'<@&{role_id}>'


def mention_channel(channel_id: str) -> str:
    return f'<#{channel_id}>'


def escaped_link(link: str) -> str:
    return f'<{link}>'


def mention_multiple_roles(role_ids) -> str:
    if len(role_ids) > 0:
        return ' '.join([mention_role(role_id) for role_id in role_ids])
    else:
        return ''


def create_image_embed(
        title: str,
        description: str,
        image_url: str,
        author_name: str,
        author_icon_url: str,
        image_width: int,
        image_height: int,
        color: int
) -> dict:
    return {
        'title': title,
        'type': 'image',
        'timestamp': pendulum.now().to_iso8601_string(),
        'description': description,
        'color': color,
        'image': {
            'url': image_url,
            'height': image_height,
            'width': image_width
        },
        'author': {
            'name': author_name,
            'icon_url': author_icon_url
        },
        'fields': []
    }
