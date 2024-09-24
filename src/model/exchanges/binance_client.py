import datetime as dt

import numpy as np
import binance as bn

from src.model.exchanges.client import Client


class BinanceClient(Client):
    intervals = {
        '1m': '1m', 1: '1m', '1': '1m',
        '3m': '3m', 3: '3m', '3': '3m',
        '5m': '5m', 5: '5m', '5': '5m',
        '15m': '15m', 15: '15m', '15': '15m',
        '30m': '30m', 30: '30m', '30': '30m',
        '1h': '1h', 60: '1h', '60': '1h',
        '2h': '2h', 120: '2h', '120': '2h',
        '4h': '4h', 240: '4h', '240': '4h',
        '6h': '6h', 360: '6h', '360': '6h',
        '12h': '12h', 720: '12h', '720': '12h',
        '1d': '1d', '1D': '1d', 'd': '1d', 'D': '1d',
        '1w': '1w', 'W': '1w',
        '1M': '1M', 'M': '1M'   
    }
    exchange = 'Binance'

    def __init__(self) -> None:
        super().__init__(
            intervals=BinanceClient.intervals,
            exchange=BinanceClient.exchange
        )
        self.create_session(callback=bn.Client, testnet=False)

    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int,
        end_time: int
    ) -> None:
        datetime1 = dt.datetime.fromtimestamp(
            start_time / 1000, tz=dt.timezone.utc
        ).strftime('%Y/%m/%d %H:%M')
        datetime2 = dt.datetime.fromtimestamp(
            end_time / 1000, tz=dt.timezone.utc
        ).strftime('%Y/%m/%d %H:%M')
        print(
            f'Запрос данных: BINANCE • {symbol} '
            f'• {interval} • {datetime1} - {datetime2}.'
        )
        self.price_data = np.array(
            self.session.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_time,
                end_str=end_time,
                klines_type=bn.enums.HistoricalKlinesType(2)
            )
        )[:-1, :6].astype(float)
        print('Данные получены.')

    def get_last_klines(
        self,
        symbol: str,
        interval: str
    ) -> None:
        print(f'Запрос данных: BINANCE • {symbol} • {interval}.')
        self.price_data = np.array(
            self.session.get_historical_klines(
                symbol=symbol,
                interval=interval,
                klines_type=bn.enums.HistoricalKlinesType(2)
            )
        )[:-1, :6].astype(float)
        print('Данные получены.')

    def get_price_precision(self, symbol: str) -> float:
        symbols_info = self.session.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][0]['tickSize'])

    def get_qty_precision(self, symbol: str) -> float:
        symbols_info = self.session.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][1]['minQty'])

    def update_data(
        self,
        symbol: str,
        interval: str
        ) -> bool | None:
        while True:
            try:
                price_data = np.array(
                    self.session.get_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        limit=2,
                        klines_type=bn.enums.HistoricalKlinesType(2)
                    )
                )[:-1, :6].astype(float)
            except Exception:
                pass
            else:
                break

        if (price_data.shape[0] == 1 and 
                price_data[0, 0] > self.price_data[-1, 0]):
            self.price_data = np.concatenate((self.price_data[1:], price_data))
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
            except Exception:
                pass
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
        except Exception:
            pass

        try:
            self.session.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except Exception:
            pass

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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
            except Exception: 
                pass
        elif hedge == 'true':
            hedge_mode = 'SHORT'

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
        except Exception: 
            pass

        try:
            self.session.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except Exception: 
            pass

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
                except Exception: 
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                except Exception: 
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                except Exception: 
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    order_info['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                'time': dt.datetime.fromtimestamp(
                    order['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                'time': dt.datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                'time': dt.datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                'time': dt.datetime.fromtimestamp(
                    order['updateTime'] / 1000,
                    tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
        except Exception as exception:
            self.send_exception(exception)

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
        except Exception as exception:
            self.send_exception(exception)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.session.futures_cancel_all_open_orders(symbol=symbol)
        except Exception as exception:
            self.send_exception(exception)

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
                        'time': dt.datetime.fromtimestamp(
                            order['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                            'exchange': 'BYBIT',
                            'type': 'лимитный ордер',
                            'status': status,
                            'side': side,
                            'symbol': order['symbol'],
                            'qty': order['origQty'],
                            'price': order['price']
                        },
                        'time': dt.datetime.fromtimestamp(
                            order['updateTime'] / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)