import logging
import os
import json


class OrderCache:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.logger = logging.getLogger(__name__)

    def load(self, symbol: str) -> dict:
        path = self._get_cache_path(symbol)

        if not os.path.exists(path):
            return {'stop_ids': [], 'limit_ids': []}

        try:
            with open(path, 'r') as file:
                data = json.load(file)

            return {
                'stop_ids': data.get('stop_ids', []),
                'limit_ids': data.get('limit_ids', [])
            }
        except Exception as e:
            self.logger.error(
                f'Failed to load cache from {path}: '
                f'{type(e).__name__} - {e}'
            )
            return {'stop_ids': [], 'limit_ids': []}

    def save(self, symbol: str, order_ids: dict) -> None:
        path = self._get_cache_path(symbol)
        data = {
            'stop_ids': order_ids.get('stop_ids', []),
            'limit_ids': order_ids.get('limit_ids', [])
        }

        try:
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.logger.error(
                f'Failed to save cache into {path}: '
                f'{type(e).__name__} - {e}'
            )

    def _get_cache_path(self, symbol: str) -> str:
        return os.path.join(self.base_dir, f'order_ids_{symbol}.json')