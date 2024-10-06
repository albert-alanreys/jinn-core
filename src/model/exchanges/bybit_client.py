import requests as rq
import datetime as dt

from pybit.unified_trading import HTTP
import numpy as np

from src.model.exchanges.database_manager import DatabaseManager
from src.model.exchanges.client import Client


class BybitClient(Client):
    intervals = {
        1: 1, '1m': 1, '1': 1,
        3: 3, '3m': 3, '3': 3,
        5: 5, '5m': 5, '5': 5,
        15: 15, '15m': 15, '15': 15,
        30: 30, '30m': 30, '30': 30,
        60: 60, '1h': 60, '60': 60,
        120: 120, '2h': 120, '120': 120,
        240: 240, '4h': 240, '240': 240,
        360: 360, '6h': 360, '360': 360,
        720: 720, '12h': 720, '720': 720,
        'D': 'D', 'd': 'D', '1d': 'D', '1D': 'D',
        'W': 'W', '1w': 'W',
        'M': 'M', '1M': 'M'
    }
    exchange = 'Bybit'

    def __init__(self) -> None:
        super().__init__(
            intervals=BybitClient.intervals,
            exchange=BybitClient.exchange
        )

        while True:
            try:
                self.session = HTTP(
                    testnet=False,
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )
            except rq.exceptions.ConnectTimeout:
                pass
            else:
                break

    def get_klines(
        self,
        symbol: str,
        interval: str | int,
        start_time: str | None = None,
        end_time: str | None = None
    ) -> None:
        if start_time and end_time:
            start_time = int(
                dt.datetime.strptime(
                    start_time, '%Y/%m/%d %H:%M'
                ).replace(tzinfo=dt.timezone.utc).timestamp()
            ) * 1000
            end_time = int(
                dt.datetime.strptime(
                    end_time, '%Y/%m/%d %H:%M'
                ).replace(tzinfo=dt.timezone.utc).timestamp()
            ) * 1000

            self.db_manager = DatabaseManager()
            self.db_manager.connect()
            klines = self.db_manager.select(
                exchange=self.exchange,
                symbol=symbol,
                interval=self.intervals[interval],
                start_time=start_time,
                end_time=end_time
            )
            query_condition = (
                start_time < klines[0][0] or
                end_time - klines[1][0] - klines[0][0] > klines[-1][0]
            ) if len(klines) > 1 else True

            if not klines or query_condition:
                self.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time,
                    end_time=end_time
                )
                self.db_manager.insert(
                    exchange=self.exchange,
                    symbol=symbol,
                    interval=self.intervals[interval],
                    klines=self.price_data
                )
            else:
                self.price_data = np.array(klines)

            self.db_manager.disconnect()
            delattr(self, "db_manager")
        else:
            self.get_last_klines(symbol, interval)

        while True:
            try:
                self.price_precision = self.get_price_precision(symbol)
                self.qty_precision = self.get_qty_precision(symbol)
            except rq.exceptions.ConnectTimeout:
                pass
            else:
                break

    def get_historical_klines(
        self,
        symbol: str,
        interval: int | str,
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
            f'Запрос данных: BYBIT • {symbol} '
            f'• {self.intervals[interval]} • {datetime1} - {datetime2}.'
        )
        price_data = np.array(
            self.session.get_kline(
                category='linear',
                symbol=symbol,
                interval=self.intervals[interval],
                start=start_time,
                limit=1000
            )['result']['list']
        )[:0:-1, :6].astype(float)

        while True:
            start_time = int(price_data[-1, 0])

            if start_time >= end_time:
                price_data = price_data[
                    : np.where(price_data[:, 0] == end_time)[0][0]
                ]
                break
            else:
                last_price_data = np.array(
                    self.session.get_kline(
                        category='linear',
                        symbol=symbol,
                        interval=self.intervals[interval],
                        start=start_time,
                        limit=1000
                    )['result']['list']
                )[-2:0:-1, :6].astype(float)

                if last_price_data.shape[0] > 0:
                    price_data = np.vstack((price_data, last_price_data))
                else:
                    break
        
        self.price_data = price_data
        print('Данные получены.')

    def get_last_klines(
        self,
        symbol: str,
        interval: int | str
    ) -> None:
        print(
            f'Запрос данных: BYBIT • {symbol} • {self.intervals[interval]}.'
        )
        self.price_data = np.array(
            self.session.get_kline(
                category='linear',
                symbol=symbol,
                interval=self.intervals[interval],
                limit=1000
            )['result']['list']
        )[:0:-1, :6].astype(float)
        print('Данные получены.')

    def get_price_precision(self, symbol: str) -> float:
        symbol_info = self.session.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['priceFilter']['tickSize'])

    def get_qty_precision(self, symbol: str) -> float:
        symbol_info = self.session.get_instruments_info(
            category="linear", symbol=symbol
        )['result']['list'][0]
        return float(symbol_info['lotSizeFilter']['qtyStep'])

    def update_data(
        self,
        symbol: str,
        interval: int | str
        ) -> bool | None:
        while True:
            try:
                price_data = np.array(
                    self.session.get_kline(
                        category='linear',
                        symbol=symbol,
                        interval=self.intervals[interval],
                        limit=2
                    )['result']['list']
                )[:0:-1, :6].astype(float)
            except Exception:
                pass
            else:
                break

        if (price_data.shape[0] == 1 and 
                price_data[0, 0] > self.price_data[-1, 0]):
            self.price_data = np.concatenate(
                (self.price_data[1:], price_data)
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
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 1

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception:
                pass

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
        except Exception:
            pass

        try:
            self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage,
            )
        except Exception:
            pass

        try:
            market_price = float(self.session.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])

            try:
                balance = float(self.session.get_wallet_balance(
                    accountType='UNIFIED', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])
            except Exception:
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
            hedge_mode = 0

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=0,
                )
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 2

            try:
                self.session.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception:
                pass

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
        except Exception:
            pass

        try:
            self.session.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=leverage,
                sellLeverage=leverage,
            )
        except Exception:
            pass

        try:
            market_price = float(self.session.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])

            try:
                balance = float(self.session.get_wallet_balance(
                    accountType='UNIFIED', coin='USDT',
                )['result']['list'][0]['coin'][0]['availableToWithdraw'])
            except Exception:
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
                except Exception:
                    pass
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
                'time': dt.datetime.fromtimestamp(
                    int(order_info['createdTime']) / 1000, tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
        except Exception as exception:
            self.send_exception(exception)

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
        except Exception as exception:
            self.send_exception(exception)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.session.cancel_all_orders(category='linear', symbol=symbol)
        except Exception as exception:
            self.send_exception(exception)

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
                        'time': dt.datetime.fromtimestamp(
                            int(main_info['updatedTime']) / 1000,
                            tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)

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
                        'time': dt.datetime.fromtimestamp(
                            int(main_info['updatedTime']) / 1000,
                            tz=dt.timezone.utc
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
        except Exception as exception:
            self.send_exception(exception)