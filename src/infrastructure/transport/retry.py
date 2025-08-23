from __future__ import annotations
from functools import wraps
from logging import getLogger
from time import sleep
from typing import Callable, Any

from requests import RequestException

from .config import CONFIG
from .exceptions import map_requests_exception


logger = getLogger(__name__)


def retry_on_failure(func: Callable) -> Callable:
    """Decorator for HTTP methods with retry logic and error handling."""

    @wraps(func)
    def wrapper(self, url: str, *args, **kwargs) -> Any:
        retry_attempts = kwargs.pop('retry_attempts', CONFIG.retry_attempts)
        retry_delay = kwargs.pop('retry_delay', CONFIG.retry_delay)
        logging = kwargs.pop('logging', CONFIG.logging)
        
        for attempt in range(retry_attempts):
            try:
                return func(self, url, *args, **kwargs)
            except RequestException as e:
                if attempt == retry_attempts - 1:
                    if logging:
                        transport_exc = map_requests_exception(e, url)
                        logger.error(
                            f'All {retry_attempts} attempts failed '
                            f'for {url}: {transport_exc}'
                        )
                    
                    return None
                
                if logging:
                    logger.warning(
                        f'Attempt {attempt + 1} failed '
                        f'for {url}, retrying...'
                    )
                
                sleep(retry_delay)
            except Exception as e:
                if logging:
                    logger.error(f'Unexpected error for {url}: {e}')
                
                return None
        
        return None
    
    return wrapper