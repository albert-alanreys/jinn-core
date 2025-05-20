from datetime import datetime, timezone
from logging import getLogger

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

        self.logger = getLogger(__name__)

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
            self.position.switch_position_mode(symbol, 3)
        else:
            self.position.switch_position_mode(symbol, 0)
            
        match margin:
            case 'cross':
                self.position.switch_margin_mode(symbol, 0)
            case 'isolated':
                self.position.switch_margin_mode(symbol, 1)

        self.position.set_leverage(symbol, str(leverage), str(leverage))
 
        try:
            qty = self._get_quantity_to_open(symbol, size, leverage)
            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Market',
                qty=str(qty),
                position_idx=(1 if hedge else 0)
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
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
            self.position.switch_position_mode(symbol, 3)
        else:
            self.position.switch_position_mode(symbol, 0)

        match margin:
            case 'cross':
                self.position.switch_margin_mode(symbol, 0)
            case 'isolated':
                self.position.switch_margin_mode(symbol, 1)

        self.position.set_leverage(symbol, str(leverage), str(leverage))

        try:
            qty = self._get_quantity_to_open(symbol, size, leverage)
            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Market',
                qty=str(qty),
                position_idx=(2 if hedge else 0)
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_close_buy(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('Sell', symbol, size)
            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Market',
                qty=str(qty),
                position_idx=(2 if hedge else 0)
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_close_sell(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('Buy', symbol, size)
            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Market',
                qty=str(qty),
                position_idx=(1 if hedge else 0)
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный ордер',
                    'status': 'исполнен',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['avgPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
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
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            price = round(round(price / p_precision) * p_precision, 8)
            qty = self._get_quantity_to_close('Sell', symbol, size)

            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Market',
                qty=str(qty),
                trigger_direction=1,
                trigger_price=str(price),
                position_idx=(1 if hedge else 0),
                reduce_only=True
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный стоп',
                    'status': 'ожидает исполнения',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['triggerPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            price = round(round(price / p_precision) * p_precision, 8)
            qty = self._get_quantity_to_close('Sell', symbol, size)

            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Market',
                qty=str(qty),
                trigger_direction=2,
                trigger_price=str(price),
                position_idx=(2 if hedge else 0),
                reduce_only=True
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'рыночный стоп',
                    'status': 'ожидает исполнения',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['triggerPrice']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            position_size = self._get_position_size('Sell', symbol)

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = (
                        self._get_orders(symbol)['result']['list']
                    )
                    limit_orders = list(
                        filter(
                            lambda x: x['orderType'] == 'Limit' and
                                x['side'] == 'Buy',
                            orders_info
                        )
                    )
                    limit_orders_qty = sum(
                        map(lambda x: float(x['qty']), limit_orders)
                    )
                    qty = position_size - limit_orders_qty
                else:
                    qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = (
                    self.market.get_tickers(symbol)['result']['list'][0]
                )
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.market.get_qty_precision(symbol)
            p_precision = self.market.get_price_precision(symbol)

            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Limit',
                qty=str(qty),
                price=str(price),
                position_idx=(2 if hedge else 0),
                reduce_only=True
            )
            order_info = self._get_orders(
                symbol, order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'лимитный ордер',
                    'status': 'ожидает исполнения',
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['price']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            position_size = self._get_position_size('Buy', symbol)

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = (
                        self._get_orders(symbol)['result']['list']
                    )
                    limit_orders = list(
                        filter(
                            lambda x: x['orderType'] == 'Limit' and
                                x['side'] == 'Sell',
                            orders_info
                        )
                    )
                    limit_orders_qty = sum(
                        map(lambda x: float(x['qty']), limit_orders)
                    )
                    qty = position_size - limit_orders_qty
                else:
                    qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = (
                    self.market.get_tickers(symbol)['result']['list'][0]
                )
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.market.get_qty_precision(symbol)
            p_precision = self.market.get_price_precision(symbol)

            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Limit',
                qty=str(qty),
                price=str(price),
                position_idx=(1 if hedge else 0),
                reduce_only=True
            )
            order_info = self._get_orders(
                symbol=symbol,
                order_id=order['result']['orderId']
            )['result']['list'][0]

            alert = {
                'message': {
                    'exchange': 'BYBIT',
                    'type': 'лимитный ордер',
                    'status': 'ожидает исполнения',
                    'side': 'продажа',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['price']
                },
                'time': datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
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
            orders_info = self._get_orders(symbol)['result']['list']
            one_sided_orders = list(
                filter(lambda x: x['side'] == side, orders_info)
            )

            for order in one_sided_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.error(f'{type(e).__name__} - {e}')
            self.send_exception(e)

    def cancel_stop(self, symbol: str, side: str) -> None:
        try:
            orders_info = self._get_orders(symbol)['result']['list']
            stop_orders = list(
                filter(
                    lambda x: x['stopOrderType'] == 'Stop' and
                        x['side'] == side,
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
                order = self._get_orders(symbol, order_id)
                order_info = order['result']['list'][0]

                if order_info['orderStatus'] == 'Untriggered':
                    active_order_ids.append(order_id)
                    continue

                if order_info['orderStatus'] == 'Filled':
                    status = 'исполнен'
                    price = order_info['avgPrice']
                else:
                    status = 'отменён'
                    price = order_info['triggerPrice']

                if order_info['side'] == 'Buy':
                    side = 'покупка'
                else:
                    side = 'продажа'

                alert = {
                    'message': {
                        'exchange': 'BYBIT',
                        'type': 'рыночный стоп',
                        'status': status,
                        'side': side,
                        'symbol': order_info['symbol'],
                        'qty': order_info['qty'],
                        'price': price
                    },
                    'time': datetime.fromtimestamp(
                        int(order_info['updatedTime']) / 1000,
                        timezone.utc
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
                order = self._get_orders(symbol, order_id)
                order_info = order['result']['list'][0]

                if order_info['orderStatus'] == 'New':
                    active_order_ids.append(order_id)
                    continue

                if order_info['orderStatus'] == 'Filled':
                    status = 'исполнен'
                else:
                    status = 'отменён'

                if order_info['side'] == 'Buy':
                    side = 'покупка'
                else:
                    side = 'продажа'

                alert = {
                    'message': {
                        'exchange': 'BYBIT',
                        'type': 'лимитный ордер',
                        'status': status,
                        'side': side,
                        'symbol': order_info['symbol'],
                        'qty': order_info['qty'],
                        'price': order_info['price']
                    },
                    'time': datetime.fromtimestamp(
                        int(order_info['updatedTime']) / 1000,
                        timezone.utc
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
        url = f'{self.base_endpoint}/v5/order/cancel-all'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
        url = f'{self.base_endpoint}/v5/order/cancel'
        params = {'category': 'linear', 'symbol': symbol, 'orderId': order_id}
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers)

    def _create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        price: str = None,
        trigger_direction: int = None,
        trigger_price: float = None,
        position_idx: int = None,
        reduce_only: bool = None
    ) -> dict:
        url = f'{self.base_endpoint}/v5/order/create'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': qty,
            'positionIdx': position_idx,

        }

        if price:
            params['price'] = price

        if trigger_direction:
            params['triggerDirection'] = trigger_direction

        if trigger_price:
            params['triggerPrice'] = trigger_price

        if reduce_only:
            params['reduceOnly'] = reduce_only

        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers)

    def _get_orders(self, symbol: str, order_id: str = None) -> dict:
        url = f'{self.base_endpoint}/v5/order/realtime'
        params = {'category': 'linear', 'symbol': symbol}

        if order_id:
            params['orderId'] = order_id

        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)

    def _get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str
    ) -> float:
        position_size = self._get_position_size(side, symbol)

        if size.endswith('%'):
            size = float(size.rstrip('%'))
            qty = position_size * size * 0.01
        elif size.endswith('u'):
            size = float(size.rstrip('u'))
            ticker_data = (
                self.market.get_tickers(symbol)['result']['list'][0]
            )
            last_price = float(ticker_data['lastPrice'])
            qty = size / last_price

        q_precision = self.market.get_qty_precision(symbol)
        return round(round(qty / q_precision) * q_precision, 8)

    def _get_quantity_to_open(
        self,
        symbol: str,
        size: str,
        leverage: int
    ) -> float:
        ticker_data = self.market.get_tickers(symbol)['result']['list'][0]
        last_price = float(ticker_data['lastPrice'])
        wallet_data = self.account.get_wallet_balance()['result']['list']
        balance = float(wallet_data[0]['coin'][0]['walletBalance'])

        if size.endswith('%'):
            size = float(size.rstrip('%'))
            qty = balance * leverage * size * 0.01 / last_price
        elif size.endswith('u'):
            size = float(size.rstrip('u'))
            qty = leverage * size / last_price

        q_precision = self.market.get_qty_precision(symbol)
        return round(round(qty / q_precision) * q_precision, 8)

    def _get_position_size(self, side: str, symbol: str) -> float:
        try:
            positions = self._get_positions(symbol)['result']['list']
            position = next(
                filter(lambda p: p['side'] == side, positions)
            )
            return float(position['size'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> dict:
        url = f'{self.base_endpoint}/v5/position/list'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)