from __future__ import annotations
from os import getenv


DEFAULT_SERVER_PORT = '1001'


def get_server_url(default_host: str = 'http://127.0.0.1') -> str:
    """
    Determines the base server URL using environment variables.

    If BASE_URL is set, it will be used as-is.
    Otherwise, the URL will be constructed using the default host
    and the SERVER_PORT value from the environment.

    Args:
        default_host: Base host to use when BASE_URL is not set

    Returns:
        str: Fully qualified server URL
    """

    base_url = getenv('BASE_URL')
    port = getenv('SERVER_PORT') or DEFAULT_SERVER_PORT

    if base_url:
        return base_url

    return f'{default_host}:{port}'
