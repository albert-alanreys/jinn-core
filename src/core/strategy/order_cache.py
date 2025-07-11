import json
import os
from logging import getLogger


class OrderCache:
    """
    Handles persistent storage and retrieval of order IDs for trading strategies.
    
    Provides methods to save and load order IDs (both stop and limit orders)
    in JSON format, organized by exchange and symbol. Automatically creates
    the cache directory if it doesn't exist.
    """

    def __init__(self, base_dir: str, exchange: str) -> None:
        """
        Initialize the order cache with storage location and exchange name.

        Args:
            base_dir: Root directory for cache storage.
            exchange: Name of the exchange. Used in cache filenames.
        """

        self.base_dir = base_dir
        self.exchange = exchange

        os.makedirs(self.base_dir, exist_ok=True)

        self.logger = getLogger(__name__)

    def load(self, symbol: str) -> dict:
        """
        Load cached order IDs for a specific trading symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').

        Returns:
            Dictionary containing:
            - stop_ids: List of active stop order IDs
            - limit_ids: List of active limit order IDs
            
            Returns empty lists for both if cache doesn't exist or is invalid.
        """

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
        except json.JSONDecodeError:
            self.logger.error(f'Failed to load JSON from {path}')
            return {'stop_ids': [], 'limit_ids': []}

    def save(self, symbol: str, order_ids: dict) -> None:
        """
        Save current order IDs to cache for a specific trading symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            order_ids: Dictionary containing:
                      - stop_ids: List of stop order IDs to cache
                      - limit_ids: List of limit order IDs to cache
        """

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
                f'Failed to write JSON to {path}: '
                f'{type(e).__name__} - {e}'
            )

    def _get_cache_path(self, symbol: str) -> str:
        """
        Generate cache file path for a trading symbol.

        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').

        Returns:
            Full path to the cache file in format:
            {base_dir}/{exchange}_{symbol}_ORDER_IDS.json
        """

        return os.path.join(
            self.base_dir, f'{self.exchange}_{symbol}_ORDER_IDS.json'
        )