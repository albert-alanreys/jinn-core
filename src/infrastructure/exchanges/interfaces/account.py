from __future__ import annotations
from abc import ABC, abstractmethod


class AccountClientInterface(ABC):
    """Interface for account operations."""
    
    @abstractmethod
    def get_wallet_balance(self) -> dict:
        """
        Retrieve wallet balance information for futures account.
        
        Returns:
            dict: Account balance information with assets array
        """
        pass