from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING

from src.core.utils.rounding import adjust
from .base import BaseClient

if TYPE_CHECKING:
    from src.services.automation.api_clients.telegram import TelegramClient
    from .account import AccountClient
    from .market import MarketClient
    from .position import PositionClient


class OrderCreationError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class TradeClient(BaseClient):
    def __init__(
        self,
        account: 'AccountClient',
        market: 'MarketClient',
        position: 'PositionClient',
        telegram: 'TelegramClient',
        alerts: list
    ) -> None:
        super().__init__()

        self.account = account
        self.market = market
        self.position = position
        self.telegram = telegram
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
            qty = self._get_quantity_to_open(symbol, size, leverage)

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
                    order_type='рыночный ордер',
                    status='исполнен',
                    side='покупка',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный ордер',
                    status='не удалось создать',
                    side='покупка',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_open(symbol, size, leverage)

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
                    order_type='рыночный ордер',
                    status='исполнен',
                    side='продажа',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный ордер',
                    status='не удалось создать',
                    side='продажа',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
        except Exception:
            self.logger.exception('Failed to execute market_open_short')

    def market_close_long(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('LONG', symbol, size, hedge)

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='рыночный ордер',
                    status='исполнен',
                    side='продажа',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный ордер',
                    status='не удалось создать',
                    side='продажа',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
        except Exception:
            self.logger.exception('Failed to execute market_close_long')

    def market_close_short(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('SHORT', symbol, size, hedge)

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='рыночный ордер',
                    status='исполнен',
                    side='покупка',
                    symbol=order_info['symbol'],
                    qty=order_info['executedQty'],
                    price=order_info['avgPrice'],
                    created_time=order_info['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный ордер',
                    status='не удалось создать',
                    side='покупка',
                    symbol=symbol,
                    qty=str(qty),
                    price=None,
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_close(
                side='LONG',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='рыночный стоп',
                    status='ожидает исполнения',
                    side='продажа',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['stopPrice'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный стоп',
                    status='не удалось создать',
                    side='продажа',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_close(
                side='SHORT',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='рыночный стоп',
                    status='ожидает исполнения',
                    side='покупка',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['stopPrice'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='рыночный стоп',
                    status='не удалось создать',
                    side='покупка',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_open(symbol, size, leverage, price)

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
                    order_type='лимитный ордер',
                    status='ожидает исполнения',
                    side='покупка',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='лимитный ордер',
                    status='не удалось создать',
                    side='покупка',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_open(symbol, size, leverage, price)

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
                    order_type='лимитный ордер',
                    status='ожидает исполнения',
                    side='продажа',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='лимитный ордер',
                    status='не удалось создать',
                    side='продажа',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_close(
                side='LONG',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='лимитный ордер',
                    status='ожидает исполнения',
                    side='продажа',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='лимитный ордер',
                    status='не удалось создать',
                    side='продажа',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
            qty = self._get_quantity_to_close(
                side='SHORT',
                symbol=symbol,
                size=size,
                hedge=hedge,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
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
                    order_type='лимитный ордер',
                    status='ожидает исполнения',
                    side='покупка',
                    symbol=order['symbol'],
                    qty=order['origQty'],
                    price=order['price'],
                    created_time=order['updateTime']
                )
            except OrderCreationError as e:
                alert = self._create_order_alert(
                    order_type='лимитный ордер',
                    status='не удалось создать',
                    side='покупка',
                    symbol=symbol,
                    qty=str(qty),
                    price=str(adjusted_price),
                    created_time=None
                )
                self.telegram.send_order_alert(alert)
                self.logger.warning(e)
                return

            self.alerts.append(alert)
            self.telegram.send_order_alert(alert)
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
                    status = 'исполнен'
                    qty = order_info['executedQty']
                    price = order_info['avgPrice']
                else:
                    status = 'отменён'
                    qty = order_info['origQty']
                    price = order_info['stopPrice']

                if order_info['side'] == 'BUY':
                    side = 'покупка'
                else:
                    side = 'продажа'

                alert = self._create_order_alert(
                    order_type='рыночный стоп',
                    status=status,
                    side=side,
                    symbol=order_info['symbol'],
                    qty=qty,
                    price=price,
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
                self.telegram.send_order_alert(alert)

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
                    status = 'исполнен'
                else:
                    status = 'отменён'

                if order_info['side'] == 'BUY':
                    side = 'покупка'
                else:
                    side = 'продажа'

                alert = self._create_order_alert(
                    order_type='лимитный ордер',
                    status=status,
                    side=side,
                    symbol=order_info['symbol'],
                    qty=order_info['origQty'],
                    price=order_info['price'],
                    created_time=order_info['updateTime']
                )
                self.alerts.append(alert)
                self.telegram.send_order_alert(alert)

            return active_order_ids
        except Exception:
            self.logger.exception('Failed to execute check_limit_orders')
            return order_ids

    def _cancel_all_orders(self, symbol: str) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.delete(url, params=params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
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
            'message': {
                'exchange': self.EXCHANGE,
                'type': order_type,
                'status': status,
                'side': side,
                'symbol': symbol,
                'qty': qty,
                'price': price
            },
            'time': order_time
        }
        return alert

    def _get_order(self, symbol: str, order_id: str) -> dict:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/order'
        params = {'symbol': symbol, 'orderId': order_id}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)

    def _get_orders(self, symbol: str) -> list:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v1/openOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)
    
    def _get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str,
        hedge: bool,
        price: float | None = None
    ) -> float:
        position_size = self._get_position_size(side, symbol, hedge)

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = position_size * size_val * 0.01
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            effective_price = price

            if price is None:
                market_data = self.market.get_tickers(symbol)
                effective_price = float(market_data['markPrice'])

            qty = size_val / effective_price

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def _get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int,
        price: float | None = None
    ) -> float:
        effective_price = price

        if price is None:
            market_data = self.market.get_tickers(symbol)
            effective_price = float(market_data['markPrice'])

        balance_info = self.account.get_wallet_balance()['assets']
        balance = float(
            next(
                filter(
                    lambda balance: balance['asset'] == 'USDT',
                    balance_info
                )
            )['availableBalance']
        )

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = balance * leverage * size_val * 0.01 / effective_price
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            qty = leverage * size_val / effective_price

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def _get_position_size(
        self,
        side: str,
        symbol: str,
        hedge: bool
    ) -> float:
        try:
            positions = self._get_positions(symbol)
            multiplier = 1 if side == 'LONG' else -1
            position_side = side if hedge else 'BOTH'
            position = next(
                filter(
                    lambda pos: pos['positionSide'] == position_side,
                    positions
                )
            )
            return multiplier * float(position['positionAmt'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> list:
        url = f'{self.FUTURES_ENDPOINT}/fapi/v3/positionRisk'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)