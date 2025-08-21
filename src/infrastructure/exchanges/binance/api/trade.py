from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

from src.shared.utils import adjust
from .base import BaseBinanceClient

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
            msg: Detailed error explanation
        """

        super().__init__(msg)


class TradeClient(BaseBinanceClient):
    """
    Client for Binance trading operations.
    
    Handles order placement, cancellation, and monitoring.
    Supports market, limit, and stop orders.
    """

    def __init__(
        self,
        account: 'AccountClient',
        market: 'MarketClient',
        position: 'PositionClient'
    ) -> None:
        """
        Initialize trade client with required dependencies.
        
        Args:
            account: Account client instance
            market: Market client instance
            position: Position client instance
        """

        super().__init__()

        self.account = account
        self.market = market
        self.position = position

        self.alerts = []
        self.logger = getLogger(__name__)

    def market_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
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
        try:
            p_precision = self.market.get_price_precision(symbol)
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
        try:
            p_precision = self.market.get_price_precision(symbol)
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

            p_precision = self.market.get_price_precision(symbol)
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

            p_precision = self.market.get_price_precision(symbol)
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
        try:
            p_precision = self.market.get_price_precision(symbol)
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
        try:
            p_precision = self.market.get_price_precision(symbol)
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
        try:
            self._cancel_all_orders(symbol)
        except Exception:
            self.logger.exception('Failed to execute cancel_all_orders')

    def cancel_orders(self, symbol: str, side: str) -> None:
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
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            dict: API response
        """

        url = f'{self.BASE_ENDPOINT}/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.delete(url, params=params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
        """
        Internal method to cancel specific order via API.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            order_id: Order ID to cancel
            
        Returns:
            dict: API response
        """

        url = f'{self.BASE_ENDPOINT}/fapi/v1/order'
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
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side ('BUY' or 'SELL')
            position_side: Position side ('LONG', 'SHORT', 'BOTH')
            order_type: Order type ('MARKET', 'LIMIT' etc.)
            qty: Order quantity
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            reduce_only: Reduce only flag
            price: Order price for limit orders
            stop_price: Stop price for stop orders
        
        Returns:
            dict: API response with order details
            
        Raises:
            OrderCreationError: If order creation fails
        """
        
        url = f'{self.BASE_ENDPOINT}/fapi/v1/order'
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
            order_type: Type of order ('market', 'limit', 'stop market')
            status: Order status ('filled', 'pending', 'cancelled', 'failed')
            side: Order side ('buy' or 'sell')
            symbol: Trading symbol (e.g., BTCUSDT)
            qty: Order quantity
            price: Order price
            created_time: Order timestamp in milliseconds
            
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
            'exchange': 'BINANCE',
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
            symbol: Trading symbol (e.g., BTCUSDT)
            order_id: Order ID to retrieve
            
        Returns:
            dict: Order information from API
        """

        url = f'{self.BASE_ENDPOINT}/fapi/v1/order'
        params = {'symbol': symbol, 'orderId': order_id}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)

    def _get_orders(self, symbol: str) -> list:
        """
        Internal method to retrieve all open orders via API.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            
        Returns:
            list: List of open orders
        """

        url = f'{self.BASE_ENDPOINT}/fapi/v1/openOrders'
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
            operation: Operation that failed (e.g., 'market_open_long')
            symbol: Trading symbol (e.g., BTCUSDT)
            error: The exception that occurred
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