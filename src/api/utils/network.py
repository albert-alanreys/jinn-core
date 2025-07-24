import os

from src.constants.network import DEFAULT_SERVER_PORT


def get_server_url(default_host: str = 'http://127.0.0.1') -> str:
    """
    Determines the base server URL using environment variables.

    If BASE_URL is set, it will be used as-is.
    Otherwise, the URL will be constructed using the default host
    and the SERVER_PORT value from the environment.

    Args:
        default_host (str): Base host to use when BASE_URL is not set.
                            Defaults to 'http://127.0.0.1'.

    Returns:
        str: Fully qualified server URL.
    """

    base_url = os.getenv('BASE_URL')
    port = os.getenv('SERVER_PORT') or DEFAULT_SERVER_PORT

    if base_url:
        return base_url

    return f'{default_host}:{port}'
