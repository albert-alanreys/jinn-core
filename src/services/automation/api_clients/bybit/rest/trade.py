from datetime import datetime, timezone
from logging import getLogger

from src.core.utils.rounding import adjust
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

    def market_open_long(
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def market_open_short(
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def market_close_long(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('Buy', symbol, size)

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def market_close_short(self, symbol: str, size: str, hedge: bool) -> None:
        try:
            qty = self._get_quantity_to_close('Sell', symbol, size)

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def market_stop_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_close(
                side='Buy',
                symbol=symbol,
                size=size,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Market',
                qty=str(qty),
                trigger_direction=2,
                trigger_price=str(adjusted_price),
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def market_stop_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_close(
                side='Sell',
                symbol=symbol,
                size=size,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Market',
                qty=str(qty),
                trigger_direction=1,
                trigger_price=str(adjusted_price),
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def limit_open_long(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
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
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_open(symbol, size, leverage, price)

            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Limit',
                qty=str(qty),
                price=str(adjusted_price),
                position_idx=(1 if hedge else 0)
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
                    'side': 'покупка',
                    'symbol': order_info['symbol'],
                    'qty': order_info['qty'],
                    'price': order_info['price']
                },
                'time': datetime.fromtimestamp(
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def limit_open_short(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        price: float,
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
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_open(symbol, size, leverage, price)

            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Limit',
                qty=str(qty),
                price=str(adjusted_price),
                position_idx=(2 if hedge else 0)
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def limit_close_long(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_close(
                side='Buy',
                symbol=symbol,
                size=size,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

            order = self._create_order(
                symbol=symbol,
                side='Sell',
                order_type='Limit',
                qty=str(qty),
                price=str(adjusted_price),
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def limit_close_short(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            p_precision = self.market.get_price_precision(symbol)
            adjusted_price = adjust(price, p_precision)
            qty = self._get_quantity_to_close(
                side='Sell',
                symbol=symbol,
                size=size,
                price=adjusted_price
            )

            if not qty:
                self.logger.info(f'No position to close for {symbol}')
                return

            order = self._create_order(
                symbol=symbol,
                side='Buy',
                order_type='Limit',
                qty=str(qty),
                price=str(adjusted_price),
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
                    timestamp=int(order_info['createdTime']) / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            }
            self.alerts.append(alert)
            self.send_telegram_alert(alert)
            return order['result']['orderId']
        except Exception as e:
            self.logger.exception('An error occurred')
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
                filter(lambda order: order['side'] == side, orders_info)
            )

            for order in one_sided_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def cancel_stop(self, symbol: str, side: str) -> None:
        try:
            orders_info = self._get_orders(symbol)['result']['list']
            stop_orders = list(
                filter(
                    lambda order:
                        order['stopOrderType'] == 'Stop' and
                        order['side'] == side,
                    orders_info
                )
            )

            for order in stop_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)

    def check_stop_orders(self, symbol: str, order_ids: list) -> list:
        active_order_ids = []

        try:
            for order_id in order_ids:
                order = self._get_orders(symbol, order_id)

                if not order['result']['list']:
                    continue

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
                        timestamp=int(order_info['updatedTime']) / 1000,
                        tz=timezone.utc
                    ).strftime('%Y/%m/%d %H:%M:%S')
                }
                self.alerts.append(alert)
                self.send_telegram_alert(alert)

            return active_order_ids
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)
            return order_ids

    def check_limit_orders(self, symbol: str, order_ids: list) -> list:
        active_order_ids = []

        try:
            for order_id in order_ids:
                order = self._get_orders(symbol, order_id)

                if not order['result']['list']:
                    continue

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
                        timestamp=int(order_info['updatedTime']) / 1000,
                        tz=timezone.utc
                    ).strftime('%Y/%m/%d %H:%M:%S')
                }
                self.alerts.append(alert)
                self.send_telegram_alert(alert)

            return active_order_ids
        except Exception as e:
            self.logger.exception('An error occurred')
            self.send_exception(e)
            return order_ids

    def _cancel_all_orders(self, symbol: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/order/cancel-all'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'POST')
        return self.post(url, params, headers=headers)

    def _cancel_order(self, symbol: str, order_id: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/order/cancel'
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
        url = f'{self.BASE_ENDPOINT}/v5/order/create'
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
        url = f'{self.BASE_ENDPOINT}/v5/order/realtime'
        params = {'category': 'linear', 'symbol': symbol}

        if order_id:
            params['orderId'] = order_id

        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)

    def _get_quantity_to_close(
        self,
        side: str,
        symbol: str,
        size: str,
        price: float | None = None
    ) -> float:
        position_size = self._get_position_size(side, symbol)

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = position_size * size_val * 0.01
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            effective_price = price

            if price is None:
                market_data = (
                    self.market.get_tickers(symbol)['result']['list'][0]
                )
                effective_price = float(market_data['lastPrice'])

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
            market_data = self.market.get_tickers(symbol)['result']['list'][0]
            effective_price = float(market_data['lastPrice'])

        wallet_data = self.account.get_wallet_balance()['result']['list']
        balance = float(wallet_data[0]['coin'][0]['walletBalance'])

        if size.endswith('%'):
            size_val = float(size.rstrip('%'))
            qty = balance * leverage * size_val * 0.01 / effective_price
        elif size.endswith('u'):
            size_val = float(size.rstrip('u'))
            qty = leverage * size_val / effective_price

        q_precision = self.market.get_qty_precision(symbol)
        return adjust(qty, q_precision)

    def _get_position_size(self, side: str, symbol: str) -> float:
        try:
            positions = self._get_positions(symbol)['result']['list']
            position = next(
                filter(lambda pos: pos['side'] == side, positions)
            )
            return float(position['size'])
        except Exception:
            return 0.0

    def _get_positions(self, symbol: str) -> dict:
        url = f'{self.BASE_ENDPOINT}/v5/position/list'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self.get_headers(params, 'GET')
        return self.get(url, params, headers)