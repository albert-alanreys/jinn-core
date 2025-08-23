from __future__ import annotations
from typing import TYPE_CHECKING

from ..base import BaseExchangeClient
from .api import AccountClient, MarketClient, PositionClient, TradeClient

if TYPE_CHECKING:
    from ..interfaces import (
        AccountClientInterface, 
        MarketClientInterface,
        PositionClientInterface, 
        TradeClientInterface
    )


class BinanceClient(BaseExchangeClient):
    """
    Main Binance client providing unified access to all trading operations.
    
    Orchestrates account, market, position, and trade clients to provide
    a comprehensive trading interface. Implements method delegation to
    allow direct access to all subclient methods.
    """

    def __init__(self) -> None:
        """
        Initialize Binance client with all subclients.
        
        Creates instances of all required clients and establishes
        dependencies between them for seamless operation.
        """

        self._account_client = AccountClient()
        self._market_client = MarketClient()
        self._position_client = PositionClient(
            account=self._account_client,
            market=self._market_client
        )
        self._trade_client = TradeClient(
            account=self._account_client,
            market=self._market_client,
            position=self._position_client
        )

    @property
    def exchange_name(self) -> str:
        """
        Get the name of the exchange.
        
        Returns:
            str: Exchange identifier
        """

        return 'BINANCE'

    @property
    def account(self) -> AccountClientInterface:
        """Access to account operations"""

        return self._account_client

    @property
    def market(self) -> MarketClientInterface:
        """Access to market operations"""  

        return self._market_client

    @property
    def position(self) -> PositionClientInterface:
        """Access to position operations"""

        return self._position_client

    @property
    def trade(self) -> TradeClientInterface:
        """Access to trade operations"""

        return self._trade_client