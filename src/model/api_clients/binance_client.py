import logging
import requests as rq
from datetime import datetime, timezone

import binance as bn
import numpy as np

import config
from src.model.enums import BinanceInterval


class BinanceClient():
    def __init__(self) -> None:
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET
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
            self.session = bn.Client(
                testnet=False,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
        except rq.exceptions.ConnectTimeout as e:
            self.logger.error(f'Error: {e}')

    def fetch_historical_klines(
        self,
        symbol: str,
        interval: BinanceInterval,
        start_time: int,
        end_time: int
    ) -> None:
        self.logger.info(
            f'Fetching data: BINANCE • {symbol} '
            f'• {interval.value} • {start_time} - {end_time}'
        )

        datetime1 = int(
            datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )
        datetime2 = int(
            datetime.strptime(end_time, '%Y-%m-%d %H:%M')
            .replace(tzinfo=timezone.utc)
            .timestamp() * 1000
        )

        self.klines = np.array(
            self.session.get_historical_klines(
                symbol=symbol,
                interval=interval.value,
                start_str=datetime1,
                end_str=datetime2,
                klines_type=bn.enums.HistoricalKlinesType(2)
            )
        )[:-1, :6].astype(float)

    def fetch_last_klines(
        self,
        symbol: str,
        interval: BinanceInterval
    ) -> None:
        self.logger.info(
            f'Fetching data: BINANCE • {symbol} • {interval.value}'
        )

        self.klines = np.array(
            self.session.get_historical_klines(
                symbol=symbol,
                interval=interval.value,
                klines_type=bn.enums.HistoricalKlinesType(2)
            )
        )[:-1, :6].astype(float)

    def fetch_price_precision(self, symbol: str) -> float:
        symbols_info = self.session.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        self.price_precision = float(symbol_info['filters'][0]['tickSize'])

    def fetch_qty_precision(self, symbol: str) -> float:
        symbols_info = self.session.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        self.qty_precision = float(symbol_info['filters'][1]['minQty'])

    def update_data(
        self,
        symbol: str,
        interval: BinanceInterval
        ) -> bool | None:
        while True:
            try:
                klines = np.array(
                    self.session.get_historical_klines(
                        symbol=symbol,
                        interval=interval.value,
                        limit=2,
                        klines_type=bn.enums.HistoricalKlinesType(2)
                    )
                )[:-1, :6].astype(float)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            else:
                break

        if (klines.shape[0] == 1 and 
                klines[0, 0] > self.klines[-1, 0]):
            self.klines = np.concatenate((self.klines[1:], klines))
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
            hedge_mode = 'BOTH'

            try:
                self.session.futures_change_position_mode(
                    dualSidePosition=False
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')
        elif hedge == 'true':
            hedge_mode = 'LONG'

            try:
                self.session.futures_change_position_mode(
                    dualSidePosition=True
                )
            except Exception:
                pass

        try:
            if margin == 'cross':
                self.session.futures_change_margin_type(
                    symbol=symbol, marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.session.futures_change_margin_type(
                    symbol=symbol, marginType='ISOLATED'
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            self.session.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            market_price = float(
                self.session.futures_mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.session.futures_account_balance()
            balance = float(
                next(
                    filter(lambda x: x['asset'] == 'USDT', balance_info)
                )['availableBalance']
            )

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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty 
            )

            while True:
                try:
                    order_info = self.session.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else:
                    break

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
                    order_info['updateTime'] / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })

            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
            hedge_mode = 'BOTH'

            try:
                self.session.futures_change_position_mode(
                    dualSidePosition=False
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')
        elif hedge == 'true':
            hedge_mode = 'SHORT'

            try:
                self.session.futures_change_position_mode(
                    dualSidePosition=True
                )
            except Exception as e:
                self.logger.error(f'Error: {e}')

        try:
            if margin == 'cross':
                self.session.futures_change_margin_type(
                    symbol=symbol, marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.session.futures_change_margin_type(
                    symbol=symbol, marginType='ISOLATED'
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            self.session.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except Exception as e:
            self.logger.error(f'Error: {e}')

        try:
            market_price = float(
                self.session.futures_mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.session.futures_account_balance()
            balance = float(
                next(
                    filter(lambda x: x['asset'] == 'USDT', balance_info)
                )['availableBalance']
            )

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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty 
            )

            while True:
                try:
                    order_info = self.session.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else: 
                    break

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
                    order_info['updateTime'] / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            while True:
                try:
                    order_info = self.session.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else: 
                    break

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
                    order_info['updateTime'] / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.session.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            while True:
                try:
                    order_info = self.session.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except Exception as e:
                    self.logger.error(f'Error: {e}')
                else: 
                    break

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
                    order_info['updateTime'] / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Исполнен рыночный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order_info['symbol']}'
                f'\n• количество — {order_info['executedQty']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='STOP_MARKET',
                quantity=qty,
                stopPrice=price,
                reduceOnly=reduce_only
            )

            self.stop_orders.append(order['orderId'])
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
                    order['updateTime'] / 1000, tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен рыночный стоп на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['stopPrice']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='STOP_MARKET',
                quantity=qty,
                stopPrice=price,
                reduceOnly=reduce_only
            )

            self.stop_orders.append(order['orderId'])
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
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен рыночный стоп на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['stopPrice']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = -float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='LIMIT',
                timeInForce='GTC',
                quantity=qty,
                price=price,
                reduceOnly=reduce_only
            )

            self.limit_orders.append(order['orderId'])
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
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен лимитный ордер на Binance:'
                f'\n• направление — покупка'
                f'\n• символ — #{order['symbol']}' 
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['price']}'
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
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.session.futures_position_information(
                symbol=symbol
            )
            position_size = float(
                next(
                    filter(
                        lambda x: x['positionSide'] == hedge_mode,
                        positions_info
                    )
                )['positionAmt']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = position_size * size * 0.01
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                market_price = float(
                    self.session.futures_mark_price(symbol=symbol)['markPrice']
                )
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
            order = self.session.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='LIMIT',
                timeInForce='GTC',
                quantity=qty,
                price=price,
                reduceOnly=reduce_only
            )

            self.limit_orders.append(order['orderId'])
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
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M:%S')
            })
            message = (
                f'Выставлен лимитный ордер на Binance:'
                f'\n• направление — продажа'
                f'\n• символ — #{order['symbol']}'
                f'\n• количество — {order['origQty']}'
                f'\n• цена — {order['price']}'
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
            orders_info = self.session.futures_get_open_orders(
                symbol=symbol
            )
            stop_orders = list(
                filter(
                    lambda x: x['type'] == 'STOP_MARKET' and
                        x['side'] == side.upper(),
                    orders_info
                )
            )

            for i in stop_orders:
                self.session.futures_cancel_order(
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
            orders_info = self.session.futures_get_open_orders(
                symbol=symbol
            )
            one_sided_orders = list(
                filter(
                    lambda x: x['side'] == side.upper(), orders_info
                )
            )

            for i in one_sided_orders:
                self.session.futures_cancel_order(
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.session.futures_cancel_all_open_orders(symbol=symbol)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_stop_status(self, symbol: str) -> None:
        try:
            for orderId in self.stop_orders.copy():
                order = self.session.futures_get_order(
                    symbol=symbol,
                    orderId=orderId
                )

                if order['status'] != 'NEW':
                    if order['status'] == 'FILLED':
                        status = 'исполнен'
                        qty = order['executedQty']
                        price = order['avgPrice']
                    else:
                        status = 'отменён'
                        qty = order['origQty']
                        price = order['stopPrice']

                    if order['side'] == 'BUY':
                        side = 'покупка'
                    else:
                        side = 'продажа'

                    self.stop_orders.remove(orderId)
                    self.alerts.append({
                        'message': {
                            'exchange': 'BINANCE',
                            'type': 'рыночный стоп',
                            'status': status,
                            'side': side,
                            'symbol': order['symbol'],
                            'qty': qty,
                            'price': price
                        },
                        'time': datetime.fromtimestamp(
                            order['updateTime'] / 1000, tz=timezone.utc
                        ).strftime('%Y/%m/%d %H:%M:%S')
                    })
                    message = (
                        f'{status.capitalize()} рыночный стоп на Binance:'
                        f'\n• направление — {side}'
                        f'\n• символ — #{order['symbol']}'
                        f'\n• количество — {qty}'
                        f'\n• цена — {price}'
                    )
                    self.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_limit_status(self, symbol: str) -> None:
        try:
            for orderId in self.limit_orders.copy():
                order = self.session.futures_get_order(
                    symbol=symbol,
                    orderId=orderId
                )

                if order['status'] != 'NEW':
                    if order['status'] == 'FILLED':
                        status = 'исполнен'
                    else:
                        status = 'отменён'

                    if order['side'] == 'BUY':
                        side = 'покупка'
                    else:
                        side = 'продажа'

                    self.limit_orders.remove(orderId)
                    self.alerts.append({
                        'message': {
                            'exchange': 'BINANCE',
                            'type': 'лимитный ордер',
                            'status': status,
                            'side': side,
                            'symbol': order['symbol'],
                            'qty': order['origQty'],
                            'price': order['price']
                        },
                        'time': datetime.fromtimestamp(
                            order['updateTime'] / 1000, tz=timezone.utc
                        ).strftime('%Y/%m/%d %H:%M:%S')
                    })
                    message = (
                        f'{status.capitalize()} лимитный ордер на Binance:'
                        f'\n• направление — {side}'
                        f'\n• символ — #{order['symbol']}'
                        f'\n• количество — {order['origQty']}'
                        f'\n• цена — {order['price']}'
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