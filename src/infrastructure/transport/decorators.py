from functools import wraps
from logging import getLogger
from requests import RequestException
from time import sleep

from .exceptions import map_requests_exception
from .config import DEFAULT_CONFIG


logger = getLogger(__name__)


def http_method(func):
    """Combined decorator for HTTP methods."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logging_enabled = kwargs.pop(
            'logging', DEFAULT_CONFIG.logging_enabled
        )
        decorated = with_error_handling(logging_enabled)(
            with_retry(logging_enabled)(func)
        )
        return decorated(*args, **kwargs)

    return wrapper


def with_retry(logging_enabled):
    """Retry decorator using default config."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = DEFAULT_CONFIG.retry

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except RequestException:
                    if attempt == config.max_attempts - 1:
                        break
                    
                    sleep(config.delay_between_attempts)

            if logging_enabled:
                logger.error(f'All {config.max_attempts} attempts failed')

            return None
        
        return wrapper
    
    return decorator


def with_error_handling(logging_enabled):
    """Error handling decorator using default config."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestException as exc:
                url = args[1] if len(args) > 1 else 'unknown'
                transport_exc = map_requests_exception(exc, str(url))

                if logging_enabled:
                    logger.error(f'Transport error: {transport_exc}')
                
                return None
            except Exception as exc:
                if logging_enabled:
                    logger.error(f'Unexpected error: {exc}')
                
                return None
            
        return wrapper
    
    return decorator