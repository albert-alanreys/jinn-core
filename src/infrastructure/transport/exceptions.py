import requests


class TransportError(Exception):
    """Base exception for transport layer errors."""
    
    def __init__(self, message: str, url: str | None = None):
        super().__init__(message)
        self.url = url


class TimeoutError(TransportError):
    """Request timeout error."""
    pass


class ConnectionError(TransportError):
    """Network connection error."""
    pass


class HttpError(TransportError):
    """HTTP error with additional context."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int, 
        url: str | None = None,
        response_text: str | None = None
    ):
        super().__init__(message, url)
        self.status_code = status_code
        self.response_text = response_text


def map_requests_exception(
        exc: requests.RequestException,
        url: str
    ) -> TransportError:
    """
    Map requests exceptions to our custom transport exceptions.

    Args:
        exc: Original requests exception
        url: URL that caused the exception
        
    Returns:
        Appropriate custom transport exception
    """
    
    if isinstance(exc, requests.exceptions.Timeout):
        return TimeoutError(f'Request timeout for {url}', url=url)
    
    if isinstance(exc, requests.exceptions.ConnectionError):
        return ConnectionError(f'Connection error for {url}: {exc}', url=url)
    
    if isinstance(exc, requests.exceptions.HTTPError):
        response = exc.response
        return HttpError(
            f'HTTP {response.status_code} error for {url}: {response.reason}',
            status_code=response.status_code,
            url=url,
            response_text=response.text,
            headers=dict(response.headers)
        )
    
    return TransportError(f'Request failed for {url}: {exc}', url=url)