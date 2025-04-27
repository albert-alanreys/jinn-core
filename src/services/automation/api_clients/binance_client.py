import hashlib
import hmac
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import config
import src.core.enums as enums
from .http_client import HttpClient
from .telegram_client import TelegramClient


class BinanceClient(HttpClient):
    intervals = {
        '1m': '1m', '1': '1m', 1: '1m',
        '5m': '5m', '5': '5m', 5: '5m',
        '15m': '15m', '15': '15m', 15: '15m',
        '30m': '30m', '30': '30m', 30: '30m',
        '1h': '1h', '60': '1h', 60: '1h',
        '2h': '2h', '120': '2h', 120: '2h',
        '4h': '4h', '240': '4h', 240: '4h',
        '6h': '6h', '360': '6h', 360: '6h',
        '12h': '12h', '720': '12h', 720: '12h',
        '1d': '1d', 'd': '1d', 'D': '1d',
    }
    interval_ms = {
        '1m': 60 * 1000,
        '5m': 5 * 60 * 1000,
        '15m': 15 * 60 * 1000,
        '30m': 30 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '2h': 2 * 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '6h': 6 * 60 * 60 * 1000,
        '12h': 12 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    }
    base_endpoint_futures = 'https://fapi.binance.com'
    base_endpoint_spot = 'https://api.binance.com'

    def __init__(self) -> None:
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET
        self.telegram_client = TelegramClient()
        self.logger = logging.getLogger(__name__)
        self.alerts = []

    def get_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: str,
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
        return klines

    def get_price_precision(self, symbol: str) -> float:
        symbols_info = self._get_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info)
        )
        return float(symbol_info['filters'][0]['tickSize'])

    def get_qty_precision(self, symbol: str) -> float:
        symbols_info = self._get_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info)
        )
        return float(symbol_info['filters'][1]['stepSize'])

    def get_valid_interval(self, interval: str | int) -> str | None:
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
            self._switch_position_mode(True)
        else:
            self._switch_position_mode(False)

        match margin:
            case 'cross':
                self._switch_margin_mode(symbol, 'CROSSED')
            case 'isolated':
                self._switch_margin_mode(symbol, 'ISOLATED')

        self._set_leverage(symbol, leverage)

        try:
            last_price = float(self._get_tickers(symbol)['markPrice'])
            balance_info = self._get_wallet_balance()['assets']
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

            qty_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / qty_precision) * qty_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty
            )
            order_info = self._get_order(symbol, order['orderId'])

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
            self._switch_position_mode(True)
        else:
            self._switch_position_mode(False)

        match margin:
            case 'cross':
                self._switch_margin_mode(symbol, 'CROSSED')
            case 'isolated':
                self._switch_margin_mode(symbol, 'ISOLATED')

        self._set_leverage(symbol, leverage)

        try:
            last_price = float(self._get_tickers(symbol)['markPrice'])
            balance_info = self._get_wallet_balance()['assets']
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

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty
            )
            order_info = self._get_order(symbol, order['orderId'])

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
            positions_info = self._get_positions(symbol)
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'SHORT' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty,
                reduce_only=(None if hedge else True)
            )
            order_info = self._get_order(symbol, order['orderId'])

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
            positions_info = self._get_positions(symbol)
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'LONG' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='MARKET',
                qty=qty,
                reduce_only=(None if hedge else True)
            )
            order_info = self._get_order(symbol, order['orderId'])

            self.alerts.append({
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
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
    ) -> int | None:
        try:
            positions_info = self._get_positions(symbol)
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'SHORT' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='BUY',
                position_side=('SHORT' if hedge else 'BOTH'),
                order_type='STOP_MARKET',
                qty=qty,
                reduce_only=(None if hedge else True),
                stop_price=price
            )

            self.alerts.append({
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
            })
            message = (
                f'Выставлен рыночный стоп на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['stopPrice']}'
            )
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int | None:
        try:
            positions_info = self._get_positions(symbol)
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'LONG' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)
            order = self._create_order(
                symbol=symbol,
                side='SELL',
                position_side=('LONG' if hedge else 'BOTH'),
                order_type='STOP_MARKET',
                qty=qty,
                reduce_only=(None if hedge else True),
                stop_price=price
            )

            self.alerts.append({
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
            })
            message = (
                f'Выставлен рыночный стоп на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['stopPrice']}'
            )
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int | None:
        try:
            positions_info = self._get_positions(symbol)
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'SHORT' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

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
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен лимитный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order['symbol']}' 
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['price']}'
            )
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: bool
    ) -> int | None:
        try:
            positions_info = self._get_positions(symbol)
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == (
                            'LONG' if hedge else 'BOTH'
                        ),
                        positions_info
                    )
                )['positionAmt']
            )

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
                last_price = float(self._get_tickers(symbol)['markPrice'])
                qty = size / last_price

            q_precision = self.get_qty_precision(symbol)
            p_precision = self.get_price_precision(symbol)
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

            self.alerts.append({
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
            })
            message = (
                f'Выставлен лимитный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['price']}'
            )
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
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
            self.logger.error(e)
            self._send_exception(e)

    def cancel_one_sided_orders(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self._get_orders(symbol)
            one_sided_orders = list(
                filter(
                    lambda x: x['side'] == side.upper(), orders_info
                )
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
                order_info = self._get_order(symbol, order_id)

                if order_info['status'] == 'NEW':
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

                order_ids.remove(order_id)
                self.alerts.append({
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
                })
                message = (
                    f'{status.capitalize()} рыночный стоп на Binance:'
                    f'\n• направление — {side}'
                    f'\n• символ — #{order_info['symbol']}'
                    f'\n• количество — {qty}'
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
                order_info = self._get_order(symbol, order_id)

                if order_info['status'] == 'NEW':
                    continue

                if order_info['status'] == 'FILLED':
                    status = 'исполнен'
                else:
                    status = 'отменён'

                if order_info['side'] == 'BUY':
                    side = 'покупка'
                else:
                    side = 'продажа'

                order_ids.remove(order_id)
                self.alerts.append({
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
                })
                message = (
                    f'{status.capitalize()} лимитный ордер на Binance:'
                    f'\n• направление — {side}'
                    f'\n• символ — #{order_info['symbol']}'
                    f'\n• количество — {order_info['origQty']}'
                    f'\n• цена — {order_info['price']}'
                )
                self.telegram_client.send_message(message)

            return order_ids
        except Exception as e:
            self.logger.error(e)
            self._send_exception(e)

    def _cancel_order(self, symbol: str, order_id: str) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/order'
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.delete(url, params=params, headers=headers)
        return response

    def _cancel_orders(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/allOpenOrders'
        params = {
            'symbol': symbol,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.delete(url, params=params, headers=headers)
        return response

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
    ) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': side,
            'positionSide': position_side,
            'type': order_type,
            'quantity': qty,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }

        if time_in_force:
            params['timeInForce'] = time_in_force

        if reduce_only:
            params['reduceOnly'] = reduce_only

        if price:
            params['price'] = price

        if stop_price:
            params['stopPrice'] = stop_price

        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.post(url, params=params, headers=headers)
        return response

    def _get_exchange_info(self) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/exchangeInfo'
        response = self.get(url)
        return response

    def _get_klines(
        self,
        market: enums.Market,
        symbol: str,
        interval: str,
        start: int = None,
        end: int = None,
        limit: int = 1000
    ) -> list | None:
        match market:
            case enums.Market.FUTURES:
                url = f'{self.base_endpoint_futures}/fapi/v1/klines'
            case enums.Market.SPOT:
                url = f'{self.base_endpoint_spot}/api/v3/klines'

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
        }

        if start:
            params['startTime'] = start

        if end:
            params['endTime'] = end

        response = self.get(url, params, logging=False)
        return response

    def _get_order(self, symbol: str, order_id: str) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/order'
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.get(url, params, headers)
        return response

    def _get_orders(self, symbol: str) -> list | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/openOrders'
        params = {
            'symbol': symbol,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.get(url, params, headers)
        return response
    
    def _get_positions(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v3/positionRisk'
        params = {
            'symbol': symbol,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.get(url, params, headers)
        return response

    def _get_tickers(self, symbol: str) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/premiumIndex'
        params = {'symbol': symbol}
        response = self.get(url, params)
        return response

    def _get_wallet_balance(self) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v3/account'
        params = {
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.get(url, params, headers)
        return response
    
    def _set_leverage(self, symbol: str, leverage: int) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/leverage'
        params = {
            'symbol': symbol,
            'leverage': leverage,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.post(
            url=url,
            params=params,
            headers=headers,
            logging=False
        )
        return response

    def _switch_margin_mode(self, symbol: str, mode: int) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/marginType'
        params = {
            'symbol': symbol,
            'marginType': mode,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.post(
            url=url,
            params=params,
            headers=headers,
            logging=False
        )
        return response

    def _switch_position_mode(self, mode: False) -> dict | None:
        url = f'{self.base_endpoint_futures}/fapi/v1/positionSide/dual'
        params = {
            'dualSidePosition': mode,
            'recvWindow': 5000,
            'timestamp': int(time.time() * 1000),
        }
        params = self._add_signature(params)
        headers = {'X-MBX-APIKEY': self.api_key}
        response = self.post(
            url=url,
            params=params,
            headers=headers,
            logging=False
        )
        return response

    def _add_signature(self, params: dict) -> dict:
        str_to_sign = '&'.join([f'{k}={v}' for k, v in params.items()])
        signature = hmac.new(
            key=self.api_secret.encode('utf-8'),
            msg=str_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        params['signature'] = signature
        return params

    def _send_exception(self, exception: Exception) -> None:
        if str(exception) != '':
            self.alerts.append({
                'message': {
                    'exchange': 'BINANCE',
                    'error': str(exception)
                },
                'time': datetime.now(
                    timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{'BINANCE'}:\n{exception}'
            self.telegram_client.send_message(message)