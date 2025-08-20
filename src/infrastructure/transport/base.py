from abc import ABC, abstractmethod
from typing import Any


class BaseHttpClient(ABC):
    """
    Abstract base class for HTTP clients.  
    Defines the interface for common HTTP methods.
    """
    
    @abstractmethod
    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | list[Any] | None:
        """
        Make a GET request with retry logic.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Request headers
            **kwargs: Extra request options
        
        Returns:
            Response data on success, or None on error
        """
        pass
    
    @abstractmethod
    def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Make a POST request with retry logic.
        
        Args:
            url: Target URL
            json: JSON payload
            params: Query parameters
            headers: Request headers
            **kwargs: Extra request options
            
        Returns:
            Response data on success, or None on error
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Make a DELETE request with retry logic.
        
        Args:
            url: Target URL
            json: JSON payload
            params: Query parameters
            headers: Request headers
            **kwargs: Extra request options
            
        Returns:
            Response data on success, or None on error
        """
        pass

    @abstractmethod
    def put(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Make a PUT request with retry logic.
        
        Args:
            url: Target URL
            json: JSON payload
            params: Query parameters
            headers: Request headers
            **kwargs: Extra request options
            
        Returns:
            Response data on success, or None on error
        """
        pass
    
    @abstractmethod
    def patch(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Make a PATCH request with retry logic.
        
        Args:
            url: Target URL
            json: JSON payload
            params: Query parameters
            headers: Request headers
            **kwargs: Extra request options
            
        Returns:
            Response data on success, or None on error
        """
        pass