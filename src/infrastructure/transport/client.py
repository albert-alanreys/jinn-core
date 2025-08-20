from typing import Any

import requests

from .base import BaseHttpClient
from .retry import retry_on_failure


class HttpClient(BaseHttpClient):
    """
    HTTP client with retry logic and error handling.
    
    Inherits from BaseHttpClient and provides concrete implementation
    using decorators for error handling and retry attempts.
    """

    @retry_on_failure
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

    @retry_on_failure
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

    @retry_on_failure
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

    @retry_on_failure
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

    @retry_on_failure
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