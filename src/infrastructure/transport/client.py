from typing import Any

import requests

from .base import BaseHttpClient
from .decorators import http_method


class HttpClient(BaseHttpClient):
    """
    HTTP client with retry logic and error handling.
    
    Inherits from BaseHttpClient and provides concrete implementation
    using decorators for error handling and retry attempts.
    """

    def __init__(self):
        super().__init__()

    @http_method
    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | list[Any] | None:
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    @http_method
    def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        response = requests.post(
            url=url,
            json=json,
            params=params,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    @http_method
    def delete(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        response = requests.delete(
            url=url,
            json=json,
            params=params,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    @http_method
    def put(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        response = requests.put(
            url=url,
            json=json,
            params=params,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    @http_method
    def patch(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        response = requests.patch(
            url=url,
            json=json,
            params=params,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()