import requests
from logging import getLogger
from time import sleep


class HttpClient:
    """
    Base HTTP client for making API requests with retry logic.
    
    Provides common HTTP methods (GET, POST, DELETE) with error handling,
    retry mechanism, and logging capabilities.
    """

    logger = getLogger(__name__)

    def get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        attempts: int = 3,
        logging: bool = True
    ) -> dict | list | None:
        """
        Make a GET request with retry logic.
        
        Args:
            url (str): Target URL for the request
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            attempts (int): Number of retry attempts
            logging (bool): Whether to log errors
            
        Returns:
            dict | list | None: Response data or None if all attempts fail
        """

        for _ in range(attempts):
            try:
                response = requests.get(
                    url=url,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if logging:
                    self.logger.error(
                        f'The request exceeded the timeout limit for {url}'
                    )
            except requests.exceptions.ConnectionError:
                if logging:
                    self.logger.error(
                        f'Connection problem while trying to reach: {url}'
                    )
            except requests.exceptions.HTTPError as e:
                if logging:
                    self.logger.error(
                        f'HTTP Error for {url}: '
                        f'{e.response.status_code} - {e.response.reason}'
                    )
            except requests.exceptions.RequestException as e:
                if logging:
                    self.logger.error(f'Request failed for {url}: {e}')

            sleep(0.5)

        return None
    
    def post(
        self,
        url: str,
        json: dict = None,
        params: dict = None,
        headers: dict = None,
        attempts: int = 3,
        logging: bool = True
    ) -> dict | None:
        """
        Make a POST request with retry logic.
        
        Args:
            url (str): Target URL for the request
            json (dict, optional): JSON payload
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            attempts (int): Number of retry attempts
            logging (bool): Whether to log errors
            
        Returns:
            dict | None: Response data or None if all attempts fail
        """

        for _ in range(attempts):
            try:
                response = requests.post(
                    url=url,
                    json=json,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if logging:
                    self.logger.error(
                        f'The request exceeded the timeout limit for {url}'
                    )
            except requests.exceptions.ConnectionError:
                if logging:
                    self.logger.error(
                        f'Connection problem while trying to reach: {url}'
                    )
            except requests.exceptions.HTTPError as e:
                if logging:
                    self.logger.error(
                        f'HTTP Error for {url}: '
                        f'{e.response.status_code} - {e.response.reason}'
                    )
            except requests.exceptions.RequestException as e:
                if logging:
                    self.logger.error(f'Request failed for {url}: {e}')

            sleep(0.5)

        return None

    def delete(
        self,
        url: str,
        json: dict = None,
        params: dict = None,
        headers: dict = None,
        attempts: int = 3,
        logging: bool = True
    ) -> dict | None:
        """
        Make a DELETE request with retry logic.
        
        Args:
            url (str): Target URL for the request
            json (dict, optional): JSON payload
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            attempts (int): Number of retry attempts
            logging (bool): Whether to log errors
            
        Returns:
            dict | None: Response data or None if all attempts fail
        """

        for _ in range(attempts):
            try:
                response = requests.delete(
                    url=url,
                    json=json,
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if logging:
                    self.logger.error(
                        f'The request exceeded the timeout limit for {url}'
                    )
            except requests.exceptions.ConnectionError:
                if logging:
                    self.logger.error(
                        f'Connection problem while trying to reach: {url}'
                    )
            except requests.exceptions.HTTPError as e:
                if logging:
                    self.logger.error(
                        f'HTTP Error for {url}: '
                        f'{e.response.status_code} - {e.response.reason}'
                    )
            except requests.exceptions.RequestException as e:
                if logging:
                    self.logger.error(f'Request failed for {url}: {e}')

            sleep(0.5)

        return None