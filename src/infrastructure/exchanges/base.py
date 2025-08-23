from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interfaces import AccountClientInterface
    from .interfaces import MarketClientInterface
    from .interfaces import PositionClientInterface
    from .interfaces import TradeClientInterface


class BaseExchangeClient(ABC):
    """
    Abstract base class for all exchange clients.
    
    Each implementation must provide account, market,
    position, and trade clients.
    """

    @property
    @abstractmethod
    def exchange_name(self) -> str:
        """Return the name of the exchange"""
        pass

    @property
    @abstractmethod
    def account(self) -> AccountClientInterface:
        """Access to account operations"""
        pass

    @property
    @abstractmethod
    def market(self) -> MarketClientInterface:
        """Access to market operations"""
        pass

    @property
    @abstractmethod
    def position(self) -> PositionClientInterface:
        """Access to position operations"""
        pass

    @property
    @abstractmethod
    def trade(self) -> TradeClientInterface:
        """Access to trade operations"""
        pass