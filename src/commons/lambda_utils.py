import os

from src.commons import common_exceptions


def get_env_var(name: str) -> str:
    """
    Get the value of an environment variable. This is a wrapper around os.getenv that raises an exception if the
    variable is not set.
    :param name: The name of the environment variable
    :return: The value of the environment variable
    :except common_exceptions.VariableNotFoundException: If the environment variable is not set
    """
    value = os.getenv(name)
    if value is None:
        raise common_exceptions.VariableNotFoundException(name)
    return value
