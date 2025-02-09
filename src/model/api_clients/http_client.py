import logging
import requests
import time


class HttpClient:
    logger = logging.getLogger(__name__)

    def get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        attempts: int = 3,
        logging: bool = True
    ) -> dict | list | None:
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

            time.sleep(0.5)

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

            time.sleep(0.5)

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

            time.sleep(0.5)

        return None