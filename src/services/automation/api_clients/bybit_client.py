import hashlib
import hmac
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import config
import src.core.enums as enums
from .http_client import HttpClient
from .telegram_client import TelegramClient


class BybitClient(HttpClient):
    intervals = {
        1: 1, '1': 1, '1m': 1,
        5: 5, '5': 5, '5m': 5,
        15: 15, '15': 15, '15m': 15,
        30: 30, '30': 30, '30m': 30,
        60: 60, '60': 60, '1h': 60,
        120: 120, '120': 120, '2h': 120,
        240: 240, '240': 240, '4h': 240,
        360: 360, '360': 360, '6h': 360,
        720: 720, '720': 720, '12h': 720,
        'D': 'D', 'd': 'D', '1d': 'D',
    }
    interval_ms = {
        1: 60 * 1000,
        5: 5 * 60 * 1000,
        15: 15 * 60 * 1000,
        30: 30 * 60 * 1000,
        60: 60 * 60 * 1000,
        120: 2 * 60 * 60 * 1000,
        240: 4 * 60 * 60 * 1000,
        360: 6 * 60 * 60 * 1000,
        720: 12 * 60 * 60 * 1000,
        'D': 24 * 60 * 60 * 1000,
    }
    base_endpoint = 'https://api.bybit.com'

    def __init__(self) -> None:
        self.api_key = config.BYBIT_API_KEY
        self.api_secret = config.BYBIT_API_SECRET
        self.telegram_client = TelegramClient()
        self.logger = logging.getLogger(__name__)
        self.alerts = []

    def get_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: str | int,
        start: str,
        end: str
    ) -> list:
        start = int(
            datetime.strptime(start, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        end = int(
            datetime.strptime(end, '%Y-%m-%d')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        interval_ms = self.interval_ms[interval]
        step = interval_ms * 1000
        time_ranges = [
            (start, min(start + step - interval_ms, end))
            for start in range(start, end, step)
        ]
        klines = []

        with ThreadPoolExecutor(max_workers=7) as executor:
            results = executor.map(
                lambda time_range: self._get_klines(
                    market=market,
                    symbol=symbol,
                    interval=interval,
                    start=time_range[0],
                    end=time_range[1]
                ),
                time_ranges
            )

            for result in results:
                klines.extend(result)

        return klines

    def get_last_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000
    ) -> list:
        klines = self._get_klines(
            market=enums.Market.FUTURES,
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        if klines is None:
            return []

        return klines

    def get_price_precision(self, symbol: str) -> float:
        symbol_info = (
            self._get_symbol_info(symbol)['result']['list'][0]
        )
        return float(symbol_info['priceFilter']['tickSize'])

    def get_qty_precision(self, symbol: str) -> float:
        symbol_info = (
            self._get_symbol_info(symbol)['result']['list'][0]
        )
        return float(symbol_info['lotSizeFilter']['qtyStep'])

    def get_valid_interval(self, interval: str | int) -> str | int | None:
        if interval in self.intervals:
            return self.intervals[interval]
        
        self.logger.error(f'Invalid interval: {interval}')

    def market_open_buy(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        if hedge:
            self._switch_position_mode(symbol, 3)
        else:
            self._switch_position_mode(symbol, 0)
            
        match margin:
            case 'cross':
                self._switch_margin_mode(symbol, 0)
            case 'isolated':
                self._switch_margin_mode(symbol, 1)

        self._set_leverage(symbol, str(leverage), str(leverage))
 
        try:
            ticker_data = self._get_tickers(symbol)['result']['list'][0]
            last_price = float(ticker_data['lastPrice'])
            wallet_data = self._get_wallet_balance()['result']['list']
            balance = float(wallet_data[0]['coin'][0]['walletBalance'])

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / last_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_open_sell(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: bool
    ) -> None:
        if hedge:
            self._switch_position_mode(symbol, 3)
        else:
            self._switch_position_mode(symbol, 0)

        match margin:
            case 'cross':
                self._switch_margin_mode(symbol, 0)
            case 'isolated':
                self._switch_margin_mode(symbol, 1)

        self._set_leverage(symbol, str(leverage), str(leverage))

        try:
            ticker_data = self._get_tickers(symbol)['result']['list'][0]
            last_price = float(ticker_data['lastPrice'])
            wallet_data = self._get_wallet_balance()['result']['list']
            balance = float(wallet_data[0]['coin'][0]['walletBalance'])

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / last_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_close_buy(
        self,
        symbol: str,
        size: str,
        hedge: bool
    ) -> None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Sell', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_close_sell(
        self,
        symbol: str,
        size: str,
        hedge: bool
    ) -> None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Buy', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_stop_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Sell', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен рыночный стоп на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['triggerPrice']}'
            )
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Buy', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен рыночный стоп на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['triggerPrice']}'
            )
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Sell', positions_info)
                )['size']
            )

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
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен лимитный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['price']}'
            )
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> str | None:
        try:
            positions_info = self._get_positions(symbol)['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Buy', positions_info)
                )['size']
            )

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
                ticker_data = self._get_tickers(symbol)['result']['list'][0]
                last_price = float(ticker_data['lastPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен лимитный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['price']}'
            )
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
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
            self.logger.error(e)
            self._send_exception(e)

    def cancel_one_sided_orders(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self._get_orders(symbol)['result']['list']
            one_sided_orders = list(
                filter(lambda x: x['side'] == side, orders_info)
            )

            for order in one_sided_orders:
                self._cancel_order(symbol, order['orderId'])
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def cancel_all_orders(self, symbol: str) -> None:
        try:
            self._cancel_orders(symbol)
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def check_stop_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                order = self._get_orders(symbol, order_id)
                order_info = order['result']['list'][0]

                if order_info['orderStatus'] == 'Untriggered':
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

                order_ids.remove(order_id)
                self.alerts.append({
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
                })
                message = (
                    f'{status.capitalize()} рыночный стоп на Bybit:'
                    f'\n• направление — {side}'
                    f'\n• символ — #{order_info['symbol']}'
                    f'\n• количество — {order_info['qty']}'
                    f'\n• цена — {price}'
                )
                self.telegram_client.send_message(message)

            return order_ids
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def check_limit_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                order = self._get_orders(symbol, order_id)
                order_info = order['result']['list'][0]

                if order_info['orderStatus'] == 'New':
                    continue

                if order_info['orderStatus'] == 'Filled':
                    status = 'исполнен'
                else:
                    status = 'отменён'

                if order_info['side'] == 'Buy':
                    side = 'покупка'
                else:
                    side = 'продажа'

                order_ids.remove(order_id)
                self.alerts.append({
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
                })
                message = (
                    f'{status.capitalize()} лимитный ордер на Bybit:'
                    f'\n• направление — {side}'
                    f'\n• символ — #{order_info['symbol']}'
                    f'\n• количество — {order_info['qty']}'
                    f'\n• цена — {order_info['price']}'
                )
                self.telegram_client.send_message(message)

            return order_ids
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def _cancel_order(self, symbol: str, order_id: str) -> dict | None:
        url = f'{self.base_endpoint}/v5/order/cancel'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'orderId': order_id,
        }
        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers)
        return response

    def _cancel_orders(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint}/v5/order/cancel-all'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers)
        return response

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
    ) -> dict | None:
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

        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers)
        return response

    def _get_klines(
        self,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> dict | None:
        url = f'{self.base_endpoint}/v5/market/kline'
        
        match market:
            case enums.Market.FUTURES:
                category = 'linear'
            case enums.Market.SPOT:
                category = 'spot'

        params = {
            'category': category,
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
        }

        if start:
            params['start'] = start

        if end:
            params['end'] = end

        response = self.get(url, params, logging=False)
        return response['result']['list'][::-1]

    def _get_orders(self, symbol: str, order_id: str = None) -> dict | None:
        url = f'{self.base_endpoint}/v5/order/realtime'
        params = {'category': 'linear', 'symbol': symbol}

        if order_id:
            params['orderId'] = order_id

        headers = self._get_headers(params, 'GET')
        response = self.get(url, params, headers)
        return response

    def _get_positions(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint}/v5/position/list'
        params = {'category': 'linear', 'symbol': symbol}
        headers = self._get_headers(params, 'GET')
        response = self.get(url, params, headers)
        return response

    def _get_tickers(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint}/v5/market/tickers'
        params = {'category': 'linear', 'symbol': symbol}
        response = self.get(url, params)
        return response

    def _get_symbol_info(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint}/v5/market/instruments-info'
        params = {'category': 'linear', 'symbol': symbol}
        response = self.get(url, params)
        return response

    def _get_wallet_balance(self) -> dict | None:
        url = f'{self.base_endpoint}/v5/account/wallet-balance'
        params = {'accountType': 'UNIFIED', 'coin': 'USDT'}
        headers = self._get_headers(params, 'GET')
        response = self.get(url, params, headers)
        return response

    def _set_leverage(
        self,
        symbol: str,
        buy_leverage: str,
        sell_leverage: str
    ) -> dict | None:
        url = f'{self.base_endpoint}/v5/position/set-leverage'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'buyLeverage': buy_leverage,
            'sellLeverage': sell_leverage
        }
        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers, logging=False)
        return response

    def _switch_margin_mode(self, symbol: str, mode: int) -> dict | None:
        url = f'{self.base_endpoint}/v5/position/switch-isolated'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'tradeMode': mode,
            'buyLeverage': '1',
            'sellLeverage': '1'

        }
        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers, logging=False)
        return response
    
    def _switch_position_mode(self, symbol: str, mode: int) -> dict | None:
        url = f'{self.base_endpoint}/v5/position/switch-mode'
        params = {
            'category': 'linear',
            'symbol': symbol,
            'mode': mode
        }
        headers = self._get_headers(params, 'POST')
        response = self.post(url, params, headers=headers, logging=False)
        return response

    def _get_headers(self, params: dict, method: str) -> dict:
        timestamp = str(int(time.time() * 1000))
        recv_window = '5000'

        match method:
            case 'GET':
                query_str = '&'.join(f'{k}={v}' for k, v in params.items())
            case 'POST':
                query_str = json.dumps(params)

        str_to_sign = f'{timestamp}{self.api_key}{recv_window}{query_str}'
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-SIGN': signature,
            'X-BAPI-RECV-WINDOW': recv_window,
        }
        return headers

    def _send_exception(self, exception: Exception) -> None:
        if str(exception) != '':
            self.alerts.append({
                'message': {
                    'exchange': 'BYBIT',
                    'error': str(exception)
                },
                'time': datetime.now(
                    timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{'BYBIT'}:\n{exception}'
            self.telegram_client.send_message(message)