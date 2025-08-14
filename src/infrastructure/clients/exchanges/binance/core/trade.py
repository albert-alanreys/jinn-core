from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

from src.core.enums import Market
from src.utils.rounding import adjust
from .base import BaseClient

if TYPE_CHECKING:
    from .account import AccountClient
    from .market import MarketClient
    from .position import PositionClient


class OrderCreationError(Exception):
    """
    Exception raised for order creation failures in trading operations.

    Signals unsuccessful order placement attempts due to invalid parameters,
    exchange restrictions, or other trading rules violations.
    Carries detailed error message for troubleshooting.
    """

    def __init__(self, msg: str) -> None:
        """
        Initialize the order creation error with diagnostic message.

        Args:
            msg (str): Detailed error explanation
        """

        super().__init__(msg)


class TradeClient(BaseClient):
    """
    Client for Binance trading operations.
    
    Handles order placement, cancellation, and monitoring for futures trading.
    Supports market, limit, and stop orders with various position modes.
    
    Instance Attributes:
        account (AccountClient): Account client
        market (MarketClient): Market client
        position (PositionClient): Position client
        alerts (list): List to store trading alerts and notifications
        logger: Logger instance for this module
    """

    def __init__(
        self,
        account: 'AccountClient',
        market: 'MarketClient',
        position: 'PositionClient',
        alerts: list
    ) -> None:
        """
        Initialize trade client with required dependencies.
        
        Args:
            account (AccountClient): Account client instance
            market (MarketClient): Market client instance
            position (PositionClient): Position client instance
            alerts (list): List for storing trading alerts
        """

        super().__init__()

        self.account = account
        self.market = market
        self.position = position
        self.alerts = alerts

        self.logger = getLogger(__name__)

    def market_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        """
        Open long position with market order.
        
        Places market buy order to open long position with specified
        size, margin mode, and leverage settings.
        
        Args:
            symbol (str): Trading symbol
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            hedge (bool): Use hedge mode for position
        """

        try:
            if hedge:
                self.position.switch_position_mode(True)
            else:
                self.position.switch_position_mode(False)

            match margin:
                case 'cross':
                    self.position.switch_margin_mode(symbol, 'CROSSED')
                case 'isolated':
                    self.position.switch_margin_mode(symbol, 'ISOLATED')

            self.position.set_leverage(symbol, leverage)

            qty = self.position.get_quantity_to_open(
                symbol=symbol,
                size=size,
                leverage=leverage
            )

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='BUY',
                    position_side=('LONG' if hedge else 'BOTH'),
                    order_type='MARKET',
                    qty=qty
                )
                order_info = self._get_order(symbol, order['orderId'])

                alert = self._create_order_alert(
                    order_type='market',
                    status='filled',
                    side='buy',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_open_long',
                    symbol=symbol,
                    error=e,
                    side='buy',
                    size=size,
                    qty=qty,
                    leverage=leverage,
                    margin=margin,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='market',
                    status='failed',
                    side='buy',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.alerts.append(alert)
                return
        except Exception:
            self.logger.exception('Failed to execute market_open_long')

    def market_open_short(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        """
        Open short position with market order.
        
        Places market sell order to open short position with specified
        size, margin mode, and leverage settings.
        
        Args:
            symbol (str): Trading symbol
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            hedge (bool): Use hedge mode for position
        """

        try:
            if hedge:
                self.position.switch_position_mode(True)
            else:
                self.position.switch_position_mode(False)

            match margin:
                case 'cross':
                    self.position.switch_margin_mode(symbol, 'CROSSED')
                case 'isolated':
                    self.position.switch_margin_mode(symbol, 'ISOLATED')

            self.position.set_leverage(symbol, leverage)

            qty = self.position.get_quantity_to_open(
                symbol=symbol,
                size=size,
                leverage=leverage
            )

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='SELL',
                    position_side=('SHORT' if hedge else 'BOTH'),
                    order_type='MARKET',
                    qty=qty
                )
                order_info = self._get_order(symbol, order['orderId'])

                alert = self._create_order_alert(
                    order_type='market',
                    status='filled',
                    side='sell',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_open_short',
                    symbol=symbol,
                    error=e,
                    side='sell',
                    size=size,
                    qty=qty,
                    leverage=leverage,
                    margin=margin,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='market',
                    status='failed',
                    side='sell',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.alerts.append(alert)
                return
        except Exception:
            self.logger.exception('Failed to execute market_open_short')

    def market_close_long(self, symbol: str, size: str, hedge: bool) -> None:
        """
        Close long position with market order.
        
        Places market sell order to close existing long position.
        Supports partial closing with size specification.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            hedge (bool): Use hedge mode for position
        """

        try:
            qty = self.position.get_quantity_to_close(
                side='LONG',
                symbol=symbol,
                size=size,
                hedge=hedge
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='SELL',
                    position_side=('LONG' if hedge else 'BOTH'),
                    order_type='MARKET',
                    qty=qty,
                    reduce_only=(None if hedge else True)
                )
                order_info = self._get_order(symbol, order['orderId'])

                alert = self._create_order_alert(
                    order_type='market',
                    status='filled',
                    side='sell',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_close_long',
                    symbol=symbol,
                    error=e,
                    side='sell',
                    size=size,
                    qty=qty,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='market',
                    status='failed',
                    side='sell',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.alerts.append(alert)
                return
        except Exception:
            self.logger.exception('Failed to execute market_close_long')

    def market_close_short(self, symbol: str, size: str, hedge: bool) -> None:
        """
        Close short position with market order.
        
        Places market buy order to close existing short position.
        Supports partial closing with size specification.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            hedge (bool): Use hedge mode for position
        """

        try:
            qty = self.position.get_quantity_to_close(
                side='SHORT',
                symbol=symbol,
                size=size,
                hedge=hedge
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='BUY',
                    position_side=('SHORT' if hedge else 'BOTH'),
                    order_type='MARKET',
                    qty=qty,
                    reduce_only=(None if hedge else True)
                )
                order_info = self._get_order(symbol, order['orderId'])

                alert = self._create_order_alert(
                    order_type='market',
                    status='filled',
                    side='buy',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_close_short',
                    symbol=symbol,
                    error=e,
                    side='buy',
                    size=size,
                    qty=qty,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='market',
                    status='failed',
                    side='buy',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.alerts.append(alert)
                return
        except Exception:
            self.logger.exception('Failed to execute market_close_short')

    def market_stop_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Place stop-loss order to close long position.
        
        Creates stop-market order that will trigger when price falls
        to specified level, closing the long position.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Stop price trigger level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created stop order
        """

        try:
            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_close(
                side='LONG',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='SELL',
                    position_side=('LONG' if hedge else 'BOTH'),
                    order_type='STOP_MARKET',
                    qty=qty,
                    reduce_only=(None if hedge else True),
                    stop_price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='stop market',
                    status='pending',
                    side='sell',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['stopPrice'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_stop_close_long',
                    symbol=symbol,
                    error=e,
                    side='sell',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='stop market',
                    status='failed',
                    side='sell',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute market_stop_close_long')

    def market_stop_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Place stop-loss order to close short position.
        
        Creates stop-market order that will trigger when price rises
        to specified level, closing the short position.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Stop price trigger level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created stop order
        """

        try:
            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_close(
                side='SHORT',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='BUY',
                    position_side=('SHORT' if hedge else 'BOTH'),
                    order_type='STOP_MARKET',
                    qty=qty,
                    reduce_only=(None if hedge else True),
                    stop_price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='stop market',
                    status='pending',
                    side='buy',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['stopPrice'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='market_stop_close_short',
                    symbol=symbol,
                    error=e,
                    side='buy',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='stop market',
                    status='failed',
                    side='buy',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute market_stop_close_short')

    def limit_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
        hedge: bool
    ) -> int:
        """
        Open long position with limit order.
        
        Places limit buy order to open long position at specified price
        with configured margin mode and leverage.
        
        Args:
            symbol (str): Trading symbol
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            price (float): Limit order price
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created limit order
        """

        try:
            if hedge:
                self.position.switch_position_mode(True)
            else:
                self.position.switch_position_mode(False)

            match margin:
                case 'cross':
                    self.position.switch_margin_mode(symbol, 'CROSSED')
                case 'isolated':
                    self.position.switch_margin_mode(symbol, 'ISOLATED')

            self.position.set_leverage(symbol, leverage)

            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_open(
                symbol=symbol,
                size=size,
                leverage=leverage,
                price=price
            )

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='BUY',
                    position_side=('LONG' if hedge else 'BOTH'),
                    order_type='LIMIT',
                    qty=str(qty),
                    time_in_force='GTC',
                    price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='limit',
                    status='pending',
                    side='buy',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='limit_open_long',
                    symbol=symbol,
                    error=e,
                    side='buy',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    leverage=leverage,
                    margin=margin,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='limit',
                    status='failed',
                    side='buy',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute limit_open_long')

    def limit_open_short(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
        hedge: bool
    ) -> int:
        """
        Open short position with limit order.
        
        Places limit sell order to open short position at specified price
        with configured margin mode and leverage.
        
        Args:
            symbol (str): Trading symbol
            size (str): Position size ('10%', '100u', etc.)
            margin (str): Margin mode ('cross' or 'isolated')
            leverage (int): Leverage multiplier
            price (float): Limit order price
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created limit order
        """

        try:
            if hedge:
                self.position.switch_position_mode(True)
            else:
                self.position.switch_position_mode(False)

            match margin:
                case 'cross':
                    self.position.switch_margin_mode(symbol, 'CROSSED')
                case 'isolated':
                    self.position.switch_margin_mode(symbol, 'ISOLATED')

            self.position.set_leverage(symbol, leverage)

            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_open(
                symbol=symbol,
                size=size,
                leverage=leverage,
                price=price
            )

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='SELL',
                    position_side=('SHORT' if hedge else 'BOTH'),
                    order_type='LIMIT',
                    qty=str(qty),
                    time_in_force='GTC',
                    price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='limit',
                    status='pending',
                    side='sell',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='limit_open_short',
                    symbol=symbol,
                    error=e,
                    side='sell',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    leverage=leverage,
                    margin=margin,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='limit',
                    status='failed',
                    side='sell',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute limit_open_short')

    def limit_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Close long position with limit order (take profit).
        
        Places take-profit order to close long position when price
        reaches specified level.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Take profit price level
            hedge (bool): Use hedge mode for position
            
        Returns:
            int: Order ID of created take profit order
        """

        try:
            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_close(
                side='LONG',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='SELL',
                    position_side=('LONG' if hedge else 'BOTH'),
                    order_type='TAKE_PROFIT',
                    qty=qty,
                    time_in_force='GTC',
                    reduce_only=(None if hedge else True),
                    price=adjusted_price,
                    stop_price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='limit',
                    status='pending',
                    side='sell',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='limit_close_long',
                    symbol=symbol,
                    error=e,
                    side='sell',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='limit',
                    status='failed',
                    side='sell',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute limit_close_long')

    def limit_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        """
        Close short position with limit order (take profit).
        
        Places take-profit order to close short position when price
        reaches specified level.
        
        Args:
            symbol (str): Trading symbol
            size (str): Amount to close ('100%', '50u', etc.)
            price (float): Take profit price level
            hedge (bool): Use hedge mode for position
        
        Returns:
            int: Order ID of created take profit order
        """

        try:
            p_precision = self.market.get_price_precision(
                market=Market.FUTURES,
                symbol=symbol
            )
            adjusted_price = adjust(price, p_precision)

            qty = self.position.get_quantity_to_close(
                side='SHORT',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                return

            try:
                order = self._create_order(
                    symbol=symbol,
                    side='BUY',
                    position_side=('SHORT' if hedge else 'BOTH'),
                    order_type='TAKE_PROFIT',
                    qty=qty,
                    time_in_force='GTC',
                    reduce_only=(None if hedge else True),
                    price=adjusted_price,
                    stop_price=adjusted_price
                )

                alert = self._create_order_alert(
                    order_type='limit',
                    status='pending',
                    side='buy',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
                self.alerts.append(alert)
            except OrderCreationError as e:
                self._log_order_warning(
                    operation='limit_close_short',
                    symbol=symbol,
                    error=e,
                    side='buy',
                    size=size,
                    qty=qty,
                    price=adjusted_price,
                    hedge=hedge
                )
                alert = self._create_order_alert(
                    order_type='limit',
                    status='failed',
                    side='buy',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.alerts.append(alert)
                return

            return order['orderId']
        except Exception:
            self.logger.exception('Failed to execute limit_close_short')

    def cancel_all_orders(self, symbol: str) -> None:
        """
        Cancel all open orders for specified symbol.
        
        Cancels all pending orders (limit, stop, etc.) for the symbol
        across all position sides.
        
        Args:
            symbol (str): Trading symbol
        """

        try:
            self._cancel_all_orders(symbol)
        except Exception:
            self.logger.exception('Failed to execute cancel_all_orders')

    def cancel_orders(self, symbol: str, side: str) -> None:
        """
        Cancel all orders for specified symbol and side.
        
        Cancels all pending orders matching the specified side
        (buy or sell) for the symbol.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side ('buy' or 'sell')
        """

        try:
            orders_info = self._get_orders(symbol)
            one_sided_orders = list(
                filter(
                    lambda order: order['side'] == side.upper(),
                    orders_info
                )
            )

            for order in one_sided_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception:
            self.logger.exception('Failed to execute cancel_orders')

    def cancel_limit_orders(self, symbol: str, side: str) -> None:
        """
        Cancel limit orders for specified symbol and side.
        
        Cancels only limit orders matching the specified side
        for the symbol.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side ('buy' or 'sell')
        """

        try:
            orders_info = self._get_orders(symbol)
            limit_orders = list(
                filter(
                    lambda order:
                        order['type'] == 'LIMIT' and
                        order['side'] == side.upper(),
                    orders_info
                )
            )

            for order in limit_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception:
            self.logger.exception('Failed to execute cancel_limit_orders')

    def cancel_stop_orders(self, symbol: str, side: str) -> None:
        """
        Cancel stop orders for specified symbol and side.
        
        Cancels only stop-market orders matching the specified side
        for the symbol.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side ('buy' or 'sell')
        """

        try:
            orders_info = self._get_orders(symbol)
            stop_orders = list(
                filter(
                    lambda order:
                        order['type'] == 'STOP_MARKET' and
                        order['side'] == side.upper(),
                    orders_info
                )
            )

            for order in stop_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception:
            self.logger.exception('Failed to execute cancel_stop_orders')

    def check_stop_orders(self, symbol: str, order_ids: list) -> list:
        """
        Check status of stop orders and update alerts.
        
        Monitors stop orders for status changes (filled, cancelled) and
        creates appropriate alerts. Returns list of still active orders.
        
        Args:
            symbol (str): Trading symbol
            order_ids (list): List of order IDs to check
            
        Returns:
            list: List of order IDs that are still active
        """

        active_order_ids = []

        try:
            for order_id in order_ids:
                order_info = self._get_order(symbol, order_id)

                if not order_info:
                    continue

                if order_info['status'] == 'NEW':
                    active_order_ids.append(order_id)
                    continue

                if order_info['status'] == 'FILLED':
                    status = 'filled'
                    qty = order_info['executedQty']
                    price = order_info['avgPrice']
                else:
                    status = 'cancelled'
                    qty = order_info['origQty']
                    price = order_info['stopPrice']

                if order_info['side'] == 'BUY':
                    side = 'buy'
                else:
                    side = 'sell'

                alert = self._create_order_alert(
                    order_type='stop market',
                    status=status,
                    side=side,
                    symbol=order_info['symbol'],
                    qty=qty,
                    price=price,
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)

            return active_order_ids
        except Exception:
            self.logger.exception('Failed to execute check_stop_orders')
            return order_ids

    def check_limit_orders(self, symbol: str, order_ids: list) -> list:
        """
        Check status of limit orders and update alerts.
        
        Monitors limit orders for status changes (filled, cancelled) and
        creates appropriate alerts. Returns list of still active orders.
        
        Args:
            symbol (str): Trading symbol
            order_ids (list): List of order IDs to check
            
        Returns:
            list: List of order IDs that are still active
        """

        active_order_ids = []

        try:
            for order_id in order_ids:
                order_info = self._get_order(symbol, order_id)

                if not order_info:
                    continue

                if order_info['status'] == 'NEW':
                    active_order_ids.append(order_id)
                    continue

                if order_info['status'] == 'FILLED':
                    status = 'filled'
                else:
                    status = 'cancelled'

                if order_info['side'] == 'BUY':
                    side = 'buy'
                else:
                    side = 'sell'

                alert = self._create_order_alert(
                    order_type='limit',
                    status=status,
                    side=side,
                    symbol=order_info['symbol'],
                    qty=order_info['origQty'],
                    price=order_info['price'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)

            return active_order_ids
        except Exception:
            self.logger.exception('Failed to execute check_limit_orders')
            return order_ids

    def _cancel_all_orders(self, symbol: str) -> dict:
        """
        Internal method to cancel all orders via API.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            dict: API response
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.delete(url, params=params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
        """
        Internal method to cancel specific order via API.
        
        Args:
            symbol (str): Trading symbol
            order_id (str): Order ID to cancel
            
        Returns:
            dict: API response
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/order'
        params = {'symbol': symbol, 'orderId': order_id}
        params, headers = self.build_signed_request(params)
        return self.delete(url, params=params, headers=headers)

    def _create_order(
        self,
        symbol: str,
        side: str,
        position_side: str,
        order_type: str,
        qty: float,
        time_in_force: str = None,
        reduce_only: str = None,
        price: float = None,
        stop_price: float = None
    ) -> dict:
        """
        Internal method to create order via API.
        
        Constructs and submits order request to Binance futures API
        with specified parameters.
        
        Args:
            symbol (str): Trading symbol
            side (str): Order side ('BUY' or 'SELL')
            position_side (str): Position side ('LONG', 'SHORT', 'BOTH')
            order_type (str): Order type ('MARKET', 'LIMIT' etc.)
            qty (float): Order quantity
            time_in_force (str, optional): Time in force ('GTC', 'IOC', 'FOK')
            reduce_only (str, optional): Reduce only flag
            price (float, optional): Order price for limit orders
            stop_price (float, optional): Stop price for stop orders
        
        Returns:
            dict: API response with order details
            
        Raises:
            OrderCreationError: If order creation fails
        """
        
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': side,
            'positionSide': position_side,
            'type': order_type,
            'quantity': qty
        }

        if time_in_force:
            params['timeInForce'] = time_in_force

        if reduce_only:
            params['reduceOnly'] = reduce_only

        if price:
            params['price'] = price

        if stop_price:
            params['stopPrice'] = stop_price

        params, headers = self.build_signed_request(params)
        response = self.post(url, params=params, headers=headers)

        if response is None:
            raise OrderCreationError('API returned invalid response')

        return response

    def _create_order_alert(
        self,
        order_type: str,
        status: str,
        side: str,
        symbol: str,
        qty: str,
        price: str | None,
        created_time: int | None
    ) -> dict:
        """
        Internal method to create alert object for order events.
        
        Formats order information into standardized alert structure
        for logging and notification purposes.
        
        Args:
            order_type (str): Type of order ('market', 'limit', 'stop market')
            status (str): Order status ('filled', 'pending',
                          'cancelled', 'failed')
            side (str): Order side ('buy' or 'sell')
            symbol (str): Trading symbol
            qty (str): Order quantity
            price (str | None): Order price
            created_time (int | None): Order timestamp in milliseconds
            
        Returns:
            dict: Formatted alert object
        """

        if created_time is not None:
            order_time = datetime.fromtimestamp(
                timestamp=created_time / 1000,
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M:%S')
        else:
            order_time = datetime.fromtimestamp(
                timestamp=datetime.now().timestamp(),
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M:%S')

        alert = {
            'exchange': self.EXCHANGE,
            'type': order_type,
            'status': status,
            'side': side,
            'symbol': symbol,
            'qty': qty,
            'price': price,
            'time': order_time
        }
        return alert

    def _get_order(self, symbol: str, order_id: str) -> dict:
        """
        Internal method to retrieve order information via API.
        
        Args:
            symbol (str): Trading symbol
            order_id (str): Order ID to retrieve
            
        Returns:
            dict: Order information from API
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/order'
        params = {'symbol': symbol, 'orderId': order_id}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)

    def _get_orders(self, symbol: str) -> list:
        """
        Internal method to retrieve all open orders via API.
        
        Args:
            symbol (str): Trading symbol
            
        Returns:
            list: List of open orders
        """

        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/openOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)
    
    def _log_order_warning(
        self,
        operation: str,
        symbol: str,
        error: Exception,
        **context
    ) -> None:
        """
        Log enhanced warning message with context information.
        
        Args:
            operation (str): Operation that failed (e.g., 'market_open_long')
            symbol (str): Trading symbol
            error (Exception): The exception that occurred
            **context: Additional context parameters
        """
        
        context_parts = []

        if 'side' in context:
            context_parts.append(f"side={context['side']}")

        if 'size' in context:
            context_parts.append(f"size={context['size']}")

        if 'qty' in context:
            context_parts.append(f"qty={context['qty']}")

        if 'price' in context:
            context_parts.append(f"price={context['price']}")

        if 'leverage' in context:
            context_parts.append(f"leverage={context['leverage']}")

        if 'margin' in context:
            context_parts.append(f"margin={context['margin']}")

        if 'hedge' in context:
            context_parts.append(f"hedge={context['hedge']}")

        warning_msg = (
            f'Order failed | '
            f'Operation: {operation} | '
            f'Symbol: {symbol} | '
            f'Error: {error} | '
            f"Context: {', '.join(context_parts)}"
        )
        self.logger.warning(warning_msg)