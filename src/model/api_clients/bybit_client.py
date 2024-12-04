import logging
import requests as rq
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import numpy as np
from pybit.unified_trading import HTTP

import config
import src.model.enums as enums


class BybitClient():
    interval_ms = {
        enums.BybitInterval.MIN_1: 60 * 1000,
        enums.BybitInterval.MIN_30: 30 * 60 * 1000,
        enums.BybitInterval.HOUR_1: 60 * 60 * 1000,
        enums.BybitInterval.HOUR_2: 2 * 60 * 60 * 1000,
        enums.BybitInterval.HOUR_4: 4 * 60 * 60 * 1000,
        enums.BybitInterval.HOUR_6: 6 * 60 * 60 * 1000,
        enums.BybitInterval.DAY_1: 24 * 60 * 60 * 1000,
    }

    def __init__(self) -> None:
        self.api_key = config.BYBIT_API_KEY
        self.api_secret = config.BYBIT_API_SECRET
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID

        self.limit_orders = []
        self.stop_orders = []
        self.alerts = []

        self.telegram_url = (
            f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        )
        self.logger = logging.getLogger(__name__)

        try:
            self.session = HTTP(
                testnet=False,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
        except rq.exceptions.ConnectTimeout as e:
            self.logger.error(f'Error: {e}')

    def fetch_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: enums.BybitInterval,
        start: int,
        end: int
    ) -> None:
        def fetch_range(start: int, end: int) -> list:
            for _ in range(3):
                try:
                    klines = self.session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval.value,
                        start=start,
                        end=end,
                        limit=1000
                    )['result']['list'][::-1]
                    return klines
                except Exception as e:
                    self.logger.error(
                        f'Failed to fetch data for range {start} - {end}: {e}'
                    )

            return []

        match market:
            case enums.Market.SPOT:
                category = 'spot'
                postfix = ''
            case enums.Market.FUTURES:
                category = 'linear'
                postfix = '.P'

        self.logger.info(
            f'Fetching data: BYBIT • {symbol}{postfix} '
            f'• {interval.value} • {start} - {end}'
        )

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

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(lambda t: fetch_range(*t), time_ranges)

            for result in results:
                klines.extend(result)

        return klines

    def fetch_last_klines(
        self,
        symbol: str,
        interval: enums.BybitInterval
    ) -> None:
        self.logger.info(
            f'Fetching data: BYBIT • {symbol} • {interval.value}'
        )

        klines = np.array(
            self.session.get_kline(
                category='linear',
                symbol=symbol,
                interval=interval.value,
                limit=1000
            )['result']['list']
        )[:0:-1, :6].astype(float)
        return klines

    def fetch_price_precision(self, symbol: str) -> float:
        symbol_info = self.session.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['priceFilter']['tickSize'])

    def fetch_qty_precision(self, symbol: str) -> float:
        symbol_info = self.session.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['lotSizeFilter']['qtyStep'])

    def update_data(
        self,
        symbol: str,
        interval: enums.BybitInterval
        ) -> bool | None:
        while True:
            try:
                klines = np.array(
                    self.session.get_kline(
                        category='linear',
                        symbol=symbol,
                        interval=interval.value,
                        limit=2
                    )['result']['list']
                )[:0:-1, :6].astype(float)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            else:
                break

        if (klines.shape[0] == 1 and 
                klines[0, 0] > self.klines[-1, 0]):
            self.klines = np.concatenate(
                (self.klines[1:], klines)
            )
            return True

    def futures_market_open_buy(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: str,
        hedge: str
    ) -> None:
        if hedge == 'false':
            hedge_mode = 0

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=0,
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')
        elif hedge == 'true':
            hedge_mode = 1

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')

        try:
            if margin == 'cross':
                self.session.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=0,
                    buyLeverage='1',
                    sellLeverage='1',
                )
            elif margin == 'isolated':
                self.session.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=1,
                    buyLeverage='1',
                    sellLeverage='1',
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage,
            )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            market_price = float(self.session.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])

            try:
                balance = float(self.session.get_wallet_balance(
                    accountType='UNIFIED', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])
            except Exception as e:
                self.logger.error(f'Error: {e}')

                balance = float(self.session.get_wallet_balance(
                    accountType='CONTRACT', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])

            if size.endswith('%'):
                leverage = int(leverage)
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                leverage = int(leverage)
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_open_sell(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: str,
        hedge: str
    ) -> None:
        if hedge == 'false':
            hedge_mode = 0

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=0,
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')
        elif hedge == 'true':
            hedge_mode = 2

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')

        try:
            if margin == 'cross':
                self.session.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=0,
                    buyLeverage='1',
                    sellLeverage='1',
                )
            elif margin == 'isolated':
                self.session.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=1,
                    buyLeverage='1',
                    sellLeverage='1',
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage,
            )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            market_price = float(self.session.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])

            try:
                balance = float(self.session.get_wallet_balance(
                    accountType='UNIFIED', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])
            except Exception as e:
                self.logger.error(f'Error: {e}')

                balance = float(self.session.get_wallet_balance(
                    accountType='CONTRACT', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])

            if size.endswith('%'):
                leverage = int(leverage)
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                leverage = int(leverage)
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_close_buy(
        self,
        symbol: str,
        size: str,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_close_sell(
        self,
        symbol: str,
        size: str,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['avgPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_stop_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    price / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=qty,
                triggerDirection=1,
                triggerPrice=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

            self.stop_orders.append(order['result']['orderId'])
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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен рыночный стоп на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['triggerPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    price / self.price_precision
                ) * self.price_precision,
                8
            )

            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=qty,
                triggerDirection=2,
                triggerPrice=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

            self.stop_orders.append(order['result']['orderId'])
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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен рыночный стоп на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['triggerPrice']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Sell', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = self.session.get_open_orders(
                        category='linear', symbol=symbol
                    )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    price / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Limit',
                qty=qty,
                price=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

            self.limit_orders.append(order['result']['orderId'])
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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен лимитный ордер на Bybit:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['price']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.session.get_positions(
                category='linear', symbol=symbol
            )['result']['list']
            position_size = float(
                next(
                    filter(lambda x: x['side'] == 'Buy', positions_info)
                )['size']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))

                if size == 100:
                    orders_info = self.session.get_open_orders(
                        category='linear', symbol=symbol
                    )['result']['list']
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
                market_price = float(self.session.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    price / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.session.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Limit',
                qty=qty,
                price=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            while True:
                try:
                    order_info = self.session.get_open_orders(
                        category='linear',
                        symbol=symbol,
                        orderId=order['result']['orderId']
                    )['result']['list'][0]
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

            self.limit_orders.append(order['result']['orderId'])
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
                    int(order_info['createdTime']) / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен лимитный ордер на Bybit:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['qty']}'
                f'\n• цена — {order_info['price']}'
            )
            self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self.session.get_open_orders(
                category='linear', symbol=symbol
            )['result']['list']
            stop_orders = list(
                filter(
                    lambda x: x['stopOrderType'] == 'Stop' and
                        x['side'] == side,
                    orders_info
                )
            )

            for i in stop_orders:
                self.session.cancel_order(
                    category='linear',
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_one_sided_orders(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self.session.get_open_orders(
                category='linear', symbol=symbol
            )['result']['list']
            one_sided_orders = list(
                filter(lambda x: x['side'] == side, orders_info)
            )

            for i in one_sided_orders:
                self.session.cancel_order(
                    category='linear',
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.session.cancel_all_orders(category='linear', symbol=symbol)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_stop_status(self, symbol: str) -> None:
        try:
            for orderId in self.stop_orders.copy():
                order = self.session.get_open_orders(
                    category="linear",
                    symbol=symbol,
                    orderId=orderId
                )
                main_info = order['result']['list'][0]

                if main_info['orderStatus'] != 'Untriggered':
                    if main_info['orderStatus'] == 'Filled':
                        status = 'исполнен'
                        price = main_info['avgPrice']
                    else:
                        status = 'отменён'
                        price = main_info['triggerPrice']

                    if main_info['side'] == 'Buy':
                        side = 'покупка'
                    else:
                        side = 'продажа'

                    self.stop_orders.remove(orderId)
                    self.alerts.append({
                        'message': {
                            'exchange': 'BYBIT',
                            'type': 'рыночный стоп',
                            'status': status,
                            'side': side,
                            'symbol': main_info['symbol'],
                            'qty': main_info['qty'],
                            'price': price
                        },
                        'time': datetime.fromtimestamp(
                            int(main_info['updatedTime']) / 1000,
                            tz=timezone.utc
                        ).strftime('%Y/%m/%d %H:%M:%S')
                    })
                    message = (
                        f'{status.capitalize()} рыночный стоп на Bybit:'
                        f'\n• направление — {side}'
                        f'\n• символ — #{main_info['symbol']}'
                        f'\n• количество — {main_info['qty']}'
                        f'\n• цена — {price}'
                    )
                    self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_limit_status(self, symbol: str) -> None:
        try:
            for orderId in self.limit_orders.copy():
                order = self.session.get_open_orders(
                    category="linear",
                    symbol=symbol,
                    orderId=orderId
                )
                main_info = order['result']['list'][0]

                if main_info['orderStatus'] != 'New':
                    if main_info['orderStatus'] == 'Filled':
                        status = 'исполнен'
                    else:
                        status = 'отменён'

                    if main_info['side'] == 'Buy':
                        side = 'покупка'
                    else:
                        side = 'продажа'

                    self.limit_orders.remove(orderId)
                    self.alerts.append({
                        'message': {
                            'exchange': 'BYBIT',
                            'type': 'лимитный ордер',
                            'status': status,
                            'side': side,
                            'symbol': main_info['symbol'],
                            'qty': main_info['qty'],
                            'price': main_info['price']
                        },
                        'time': datetime.fromtimestamp(
                            int(main_info['updatedTime']) / 1000,
                            tz=timezone.utc
                        ).strftime('%Y/%m/%d %H:%M:%S')
                    })
                    message = (
                        f'{status.capitalize()} лимитный ордер на Bybit:'
                        f'\n• направление — {side}'
                        f'\n• символ — #{main_info['symbol']}'
                        f'\n• количество — {main_info['qty']}'
                        f'\n• цена — {main_info['price']}'
                    )
                    self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def send_exception(
        self,
        exception: Exception
    ) -> None:
        if str(exception) != '':
            self.alerts.append({
                'message': {
                    'api': self.api,
                    'error': str(exception)
                },
                'time': datetime.now(
                    timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{self.api}:\n{exception}'
            self.send_message(message)

    def send_message(self, message: str) -> None:
        try:
            if self.bot_token:
                rq.post(
                    self.telegram_url,
                    {'chat_id': self.chat_id, 'text': message}
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')