import logging
from datetime import datetime, timezone

from .account import AccountClient
from .base import BaseClient
from .market import MarketClient
from .position import PositionClient


class TradeClient(BaseClient):
    def __init__(
        self,
        account: AccountClient,
        market: MarketClient,
        position: PositionClient,
        alerts: list
    ) -> None:
        super().__init__(alerts)

        self.logger = logging.getLogger(__name__)

        self.account = account
        self.market = market
        self.position = position
        self.alerts = alerts

    def market_open_buy(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
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

        try:
            qty = self._get_quantity_to_open(symbol, size, leverage)
            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty
            )
            order_info = self._get_order(symbol, order['orderId'])

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['executedQty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_open_sell(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
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

        try:
            qty = self._get_quantity_to_open(symbol, size, leverage)
            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty
            )
            order_info = self._get_order(symbol, order['orderId'])

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['executedQty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_close_buy(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('SHORT', symbol, size, hedge)
            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty,
                reduce_only=(None if hedge else True)
            )
            order_info = self._get_order(symbol, order['orderId'])

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['executedQty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_close_sell(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('LONG', symbol, size, hedge)
            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty,
                reduce_only=(None if hedge else True)
            )
            order_info = self._get_order(symbol, order['orderId'])

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['executedQty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_stop_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        try:
            p_precision = self.market.get_price_precision(symbol)
            price = round(round(price / p_precision) * p_precision, 8)
            qty = self._get_quantity_to_close('SHORT', symbol, size, hedge)

            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='STOP_MARKET',
                qty=qty,
                reduce_only=(None if hedge else True),
                stop_price=price
            )

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный стоп',
                    'status': 'ожидает исполнения',
                    'side': 'покупка',
                    'symbol': order['symbol'],
                    'qty': order['origQty'],
                    'price': order['stopPrice']
                },
                'time': datetime.fromtimestamp(
                    order['updateTime'] / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        try:
            p_precision = self.market.get_price_precision(symbol)
            price = round(round(price / p_precision) * p_precision, 8)
            qty = self._get_quantity_to_close('LONG', symbol, size, hedge)

            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='STOP_MARKET',
                qty=qty,
                reduce_only=(None if hedge else True),
                stop_price=price
            )

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'рыночный стоп',
                    'status': 'ожидает исполнения',
                    'side': 'продажа',
                    'symbol': order['symbol'],
                    'qty': order['origQty'],
                    'price': order['stopPrice']
                },
                'time': datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        try:
            position_size = self._get_position_size('SHORT', symbol, hedge)

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = self._get_orders(symbol)
                    limit_orders = list(
                        filter(
                            lambda x: (
                                x['type'] == 'LIMIT' and
                                x['side'] == 'SELL'
                            ),
                            orders_info
                        )
                    )
                    limit_orders_qty = sum(
                        map(lambda x: float(x['origQty']), limit_orders)
                    )
                    qty = position_size - limit_orders_qty
                else:
                    qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(
                    self.market.get_tickers(symbol)['markPrice']
                )
                qty = size / last_price

            q_precision = self.market.get_qty_precision(symbol)
            p_precision = self.market.get_price_precision(symbol)

            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='LIMIT',
                qty=qty,
                time_in_force='GTC',
                reduce_only=(None if hedge else True),
                price=price
            )

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'лимитный ордер',
                    'status': 'ожидает исполнения',
                    'side': 'покупка',
                    'symbol': order['symbol'],
                    'qty': order['origQty'],
                    'price': order['price']
                },
                'time': datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int:
        try:
            position_size = self._get_position_size('LONG', symbol, hedge)

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = self._get_orders(symbol)
                    limit_orders = list(
                        filter(
                            lambda x: (
                                x['type'] == 'LIMIT' and
                                x['side'] == 'SELL'
                            ),
                            orders_info
                        )
                    )
                    limit_orders_qty = sum(
                        map(lambda x: float(x['origQty']), limit_orders)
                    )
                    qty = position_size - limit_orders_qty
                else:
                    qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(
                    self.market.get_tickers(symbol)['markPrice']
                )
                qty = size / last_price

            q_precision = self.market.get_qty_precision(symbol)
            p_precision = self.market.get_price_precision(symbol)

            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='LIMIT',
                qty=qty,
                time_in_force='GTC',
                reduce_only=(None if hedge else True),
                price=price
            )

            alert = {
                'message': {
                    'exchange': 'BINANCE',
                    'type': 'лимитный ордер',
                    'status': 'ожидает исполнения',
                    'side': 'продажа',
                    'symbol': order['symbol'],
                    'qty': order['origQty'],
                    'price': order['price']
                },
                'time': datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def cancel_all_orders(self, symbol: str) -> None:
        try:
            self._cancel_all_orders(symbol)
        except Exception as e:
            self.send_exception(e)

    def cancel_orders(self, symbol: str, side: str) -> None:
        try:
            orders_info = self._get_orders(symbol)
            one_sided_orders = list(
                filter(
                    lambda x: x['side'] == side.upper(),
                    orders_info
                )
            )

            for order in one_sided_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def cancel_stop(self, symbol: str, side: str) -> None:
        try:
            orders_info = self._get_orders(symbol)
            stop_orders = list(
                filter(
                    lambda x: x['type'] == 'STOP_MARKET' and
                        x['side'] == side.upper(),
                    orders_info
                )
            )

            for order in stop_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def check_stop_orders(self, symbol: str, order_ids: list) -> list:
        active_order_ids = []

        try:
            for order_id in order_ids:
                order_info = self._get_order(symbol, order_id)

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

                alert = {
                    'message': {
                        'exchange': 'BINANCE',
                        'type': 'рыночный стоп',
                        'status': status,
                        'side': side,
                        'symbol': order_info['symbol'],
                        'qty': qty,
                        'price': price
                    },
                    'time': datetime.fromtimestamp(
                        order_info['updateTime'] / 1000, timezone.utc
                    ).strftime('%Y/%m/%d %H:%M:%S')
                }
                self.alerts.append(alert)
                self.send_telegram_alert(alert)

            return active_order_ids
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)
            return order_ids

    def check_limit_orders(self, symbol: str, order_ids: list) -> list:
        active_order_ids = []

        try:
            for order_id in order_ids:
                order_info = self._get_order(symbol, order_id)

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

                alert = {
                    'message': {
                        'exchange': 'BINANCE',
                        'type': 'лимитный ордер',
                        'status': status,
                        'side': side,
                        'symbol': order_info['symbol'],
                        'qty': order_info['origQty'],
                        'price': order_info['price']
                    },
                    'time': datetime.fromtimestamp(
                        order_info['updateTime'] / 1000, timezone.utc
                    ).strftime('%Y/%m/%d %H:%M:%S')
                }
                self.alerts.append(alert)
                self.send_telegram_alert(alert)

            return active_order_ids
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)
            return order_ids

    def _cancel_all_orders(self, symbol: str) -> dict:
        url = f'{self.futures_endpoint}/fapi/v1/allOpenOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.delete(url, params=params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
        url = f'{self.futures_endpoint}/fapi/v1/order'
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
        url = f'{self.futures_endpoint}/fapi/v1/order'
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
        return self.post(url, params=params, headers=headers)
    
    def _get_order(self, symbol: str, order_id: str) -> dict:
        url = f'{self.futures_endpoint}/fapi/v1/order'
        params = {'symbol': symbol, 'orderId': order_id}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)

    def _get_orders(self, symbol: str) -> list:
        url = f'{self.futures_endpoint}/fapi/v1/openOrders'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)
    
    def _get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str,
        hedge: bool
    ) -> float:
        position_size = self._get_position_size(side, symbol, hedge)

        if size.endswith('%'):
            size = float(size.rstrip('%'))
            qty = position_size * size * 0.01
        elif size.endswith('u'):
            size = float(size.rstrip('u'))
            last_price = float(
                self.market.get_tickers(symbol)['markPrice']
            )
            qty = size / last_price

        q_precision = self.market.get_qty_precision(symbol)
        return round(round(qty / q_precision) * q_precision, 8)

    def _get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int
    ) -> float:
        last_price = float(self.market.get_tickers(symbol)['markPrice'])
        balance_info = self.account.get_wallet_balance()['assets']
        balance = float(
            next(
                filter(lambda x: x['asset'] == 'USDT', balance_info)
            )['availableBalance']
        )

        if size.endswith('%'):
            size = float(size.rstrip('%'))
            qty = balance * leverage * size * 0.01 / last_price
        elif size.endswith('u'):
            size = float(size.rstrip('u'))
            qty = leverage * size / last_price

        q_precision = self.market.get_qty_precision(symbol)
        return round(round(qty / q_precision) * q_precision, 8)
    
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
                    lambda p: p['positionSide'] == position_side,
                    positions
                )
            )
            return multiplier * float(position['positionAmt'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> list:
        url = f'{self.futures_endpoint}/fapi/v3/positionRisk'
        params = {'symbol': symbol}
        params, headers = self.build_signed_request(params)
        return self.get(url, params, headers)