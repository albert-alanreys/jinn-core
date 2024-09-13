import datetime as dt
import requests as rq
import os

import binance as bn
import numpy as np


class BinanceHTTPClient():
    def __init__(self):
        with open(os.path.abspath('.env'), 'r') as file:
            data = file.read()
            self.api_key = data[
                data.rfind('BINANCE_API_KEY=') + 16 :
                data.find('\nBINANCE_API_SECRET')
            ]
            self.api_secret = data[
                data.rfind('BINANCE_API_SECRET=') + 19 :
                data.find('\n\nTELEGRAM_BOT_TOKEN')
            ]
            self.bot_token = data[
                data.rfind('TELEGRAM_BOT_TOKEN=') + 19 :
                data.find('\nTELEGRAM_CHAT_ID')
            ]
            self.chat_id = data[
                data.rfind('TELEGRAM_CHAT_ID=') + 17 :
                data.find('\nBASE_URL')
            ].rstrip()

        self.client = bn.Client(
            testnet=False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        self.kline_intervals = {
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
            '1d': '1d', 'D': '1d',
            '1w': '1w', 'W': '1w',
            '1M': '1M', 'M': '1M'   
        }
        self.limit_orders = []
        self.stop_orders = []
        self.alerts = []

    def get_historical_klines(self, symbol, interval, start_time, end_time):
        file = (
            os.path.abspath('src/database') +
            '/binance_' + symbol + '_' + self.interval +
            '_' + str(start_time) + '_' + str(end_time) + '.npy'
        )

        try:
            self.price_data = np.load(file)
        except:
            datetime1 = dt.datetime.fromtimestamp(
                start_time / 1000, tz=dt.timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            datetime2 = dt.datetime.fromtimestamp(
                end_time / 1000, tz=dt.timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            print(
                'Запрос данных: BINANCE • {} • {} • {} - {}.'.format(
                    symbol, interval, datetime1, datetime2
                )
            )
            self.price_data = np.array(
                self.client.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    start_str=start_time,
                    end_str=end_time,
                    klines_type=bn.enums.HistoricalKlinesType(2)
                )
            )[:-1, :6].astype(float)
            np.save(file, self.price_data)
            print('Данные получены.')

    def get_last_klines(self, symbol, interval):
        print(
            'Запрос данных: BINANCE • {} • {}.'.format(symbol, interval)
        )
        self.price_data = np.array(
            self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                klines_type=bn.enums.HistoricalKlinesType(2)
            )
        )[:-1, :6].astype(float)
        print('Данные получены.')

    def get_price_precision(self, symbol):
        symbols_info = self.client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][0]['tickSize'])

    def get_qty_precision(self, symbol):
        symbols_info = self.client.futures_exchange_info()['symbols']
        symbol_info = next(
            filter(lambda x: x['symbol'] == symbol, symbols_info))
        return float(symbol_info['filters'][1]['minQty'])

    def get_data(self, symbol, interval, start_time=None, end_time=None):
        self.symbol = symbol
        self.interval = self.kline_intervals[interval]

        if start_time is not None and end_time is not None:
            self.start_time = int(
                dt.datetime.strptime(
                    start_time, '%Y/%m/%d %H:%M'
                ).replace(tzinfo=dt.timezone.utc).timestamp()
            ) * 1000
            self.end_time = int(
                dt.datetime.strptime(
                    end_time, '%Y/%m/%d %H:%M'
                ).replace(tzinfo=dt.timezone.utc).timestamp()
            ) * 1000
            self.get_historical_klines(
                self.symbol, self.interval, self.start_time, self.end_time
            )
        else:
            self.get_last_klines(self.symbol, self.interval)

        self.price_precision = self.get_price_precision(symbol)
        self.qty_precision = self.get_qty_precision(symbol)

    def update_data(self):
        while True:
            try:
                price_data = np.array(
                    self.client.get_historical_klines(
                        self.symbol, self.interval, limit=2,
                        klines_type=bn.enums.HistoricalKlinesType(2)
                    )
                )[:-1, :6].astype(float)
            except:
                pass
            else:
                break

        if (price_data.shape[0] == 1 and 
                price_data[0, 0] > self.price_data[-1, 0]):
            self.price_data = np.concatenate((self.price_data[1:], price_data))
            return True

    def futures_market_open_buy(self, symbol, size, margin, leverage, hedge):
        if hedge == 'false':
            hedge_mode = 'BOTH'

            try:
                self.client.futures_change_position_mode(
                    dualSidePosition=False
                )
            except:
                pass
        elif hedge == 'true':
            hedge_mode = 'LONG'

            try:
                self.client.futures_change_position_mode(
                    dualSidePosition=True
                )
            except:
                pass

        try:
            if margin == 'cross':
                self.client.futures_change_margin_type(
                    symbol=symbol, marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.client.futures_change_margin_type(
                    symbol=symbol, marginType='ISOLATED'
                )
        except:
            pass

        try:
            self.client.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except:
            pass

        try:
            market_price = float(
                self.client.futures_mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.client.futures_account_balance()
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
            order = self.client.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty 
            )

            while True:
                try:
                    order_info = self.client.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except:
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
                'Исполнен рыночный ордер на Binance:' +
                '\n• направление — покупка' +
                '\n• символ — #' + order_info['symbol'] +
                '\n• количество — ' + order_info['executedQty'] +
                '\n• цена — ' + order_info['avgPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_market_open_sell(self, symbol, size, margin, leverage, hedge):
        if hedge == 'false':
            hedge_mode = 'BOTH'

            try:
                self.client.futures_change_position_mode(
                    dualSidePosition=False
                )
            except: 
                pass
        elif hedge == 'true':
            hedge_mode = 'SHORT'

            try:
                self.client.futures_change_position_mode(
                    dualSidePosition=True
                )
            except: 
                pass

        try:
            if margin == 'cross':
                self.client.futures_change_margin_type(
                    symbol=symbol, marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.client.futures_change_margin_type(
                    symbol=symbol, marginType='ISOLATED'
                )
        except: 
            pass

        try:
            self.client.futures_change_leverage(
                symbol=symbol, leverage=leverage
            )
        except: 
            pass

        try:
            market_price = float(
                self.client.futures_mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.client.futures_account_balance()
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
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty 
            )

            while True:
                try:
                    order_info = self.client.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except: 
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
                'Исполнен рыночный ордер на Binance:' +
                '\n• направление — продажа' +
                '\n• символ — #' + order_info['symbol'] +
                '\n• количество — ' + order_info['executedQty'] +
                '\n• цена — ' + order_info['avgPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_market_close_buy(self, symbol, size, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.client.futures_create_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            while True:
                try:
                    order_info = self.client.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except: 
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
                'Исполнен рыночный ордер на Binance:' +
                '\n• направление — покупка' +
                '\n• символ — #' +  order_info['symbol'] +
                '\n• количество — ' + order_info['executedQty'] +
                '\n• цена — ' + order_info['avgPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_market_close_sell(self, symbol, size, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            order = self.client.futures_create_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            while True:
                try:
                    order_info = self.client.futures_get_order(
                        symbol=symbol,
                        orderId=order['orderId']
                    )
                except: 
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
                'Исполнен рыночный ордер на Binance:' +
                '\n• направление — продажа' +
                '\n• символ — #' +  order_info['symbol'] +
                '\n• количество — ' + order_info['executedQty'] +
                '\n• цена — ' + order_info['avgPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_market_stop_buy(self, symbol, size, price, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    float(price) / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.client.futures_create_order(
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
                'Выставлен рыночный стоп на Binance:' +
                '\n• направление — покупка' +
                '\n• символ — #' + order['symbol'] +
                '\n• количество — ' + order['origQty'] +
                '\n• цена — ' + order['stopPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_market_stop_sell(self, symbol, size, price, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    float(price) / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.client.futures_create_order(
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
                'Выставлен рыночный стоп на Binance:' +
                '\n• направление — продажа' +
                '\n• символ — #' + order['symbol'] +
                '\n• количество — ' + order['origQty'] +
                '\n• цена — ' + order['stopPrice']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}

            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_limit_take_buy(self, symbol, size, price, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    float(price) / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.client.futures_create_order(
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
                'Выставлен лимитный ордер на Binance:' +
                '\n• направление — покупка' +
                '\n• символ — #' + order['symbol'] +
                '\n• количество — ' + order['origQty'] +
                '\n• цена — ' + order['price']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_limit_take_sell(self, symbol, size, price, hedge):
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.client.futures_position_information(
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
                    self.client.futures_mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            qty = round(
                round(qty / self.qty_precision) * self.qty_precision, 8
            )
            price = round(
                round(
                    float(price) / self.price_precision
                ) * self.price_precision,
                8
            )
            order = self.client.futures_create_order(
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
                'Выставлен лимитный ордер на Binance:' +
                '\n• направление — продажа' +
                '\n• символ — #' + order['symbol'] +
                '\n• количество — ' + order['origQty'] +
                '\n• цена — ' + order['price']
            )
            url = (
                'https://api.telegram.org/bot' +
                self.bot_token + '/sendMessage'
            )
            data = {'chat_id': self.chat_id, 'text': message}
            
            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break
        except Exception as exception:
            self.send_exception(exception)

    def futures_cancel_stop(self, symbol, side):
        try:
            orders_info = self.client.futures_get_open_orders(
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
                self.client.futures_cancel_order(
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as exception:
            self.send_exception(exception)

    def futures_cancel_one_sided_orders(self, symbol, side):
        try:
            orders_info = self.client.futures_get_open_orders(
                symbol=symbol
            )
            one_sided_orders = list(
                filter(
                    lambda x: x['side'] == side.upper(), orders_info
                )
            )

            for i in one_sided_orders:
                self.client.futures_cancel_order(
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as exception:
            self.send_exception(exception)

    def futures_cancel_all_orders(self, symbol):
        try:
            self.client.futures_cancel_all_open_orders(symbol=symbol)
        except Exception as exception:
            self.send_exception(exception)

    def send_exception(self, exception):
        if str(exception) != '':
            self.alerts.append({
                'message': {
                    'exchange': 'BINANCE',
                    'error': str(exception)
                },
                'time': dt.datetime.now(
                    dt.timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })

            url = (
                'https://api.telegram.org/bot'
                + self.bot_token + '/sendMessage'
            )
            data = {
                'chat_id': self.chat_id,
                'text': f'❗️Binance:\n{exception}'
            }

            if self.bot_token:
                while True:
                    try: 
                        rq.post(url, data=data)
                    except: 
                        pass
                    else: 
                        break

    def check_stop_status(self, symbol):
        try:
            for orderId in self.stop_orders.copy():
                order = self.client.futures_get_order(
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
                        status.capitalize() + ' рыночный стоп на Binance:' +
                        '\n• направление — ' + side +
                        '\n• символ — #' + order['symbol'] +
                        '\n• количество — ' + qty +
                        '\n• цена — ' + price
                    )
                    url = (
                        'https://api.telegram.org/bot'
                        + self.bot_token + '/sendMessage'
                    )
                    data = {'chat_id': self.chat_id, 'text': message}
                    
                    if self.bot_token:
                        while True:
                            try: 
                                rq.post(url, data=data)
                            except: 
                                pass
                            else: 
                                break
        except Exception as exception:
            self.send_exception(exception)

    def check_limit_status(self, symbol):
        try:
            for orderId in self.limit_orders.copy():
                order = self.client.futures_get_order(
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
                        status.capitalize() + ' лимитный ордер на Bybit:' +
                        '\n• направление — ' + side +
                        '\n• символ — #' + order['symbol'] +
                        '\n• количество — ' + order['origQty'] +
                        '\n• цена — ' + order['price']
                    )
                    url = (
                        'https://api.telegram.org/bot'
                        + self.bot_token + '/sendMessage'
                    )
                    data = {'chat_id': self.chat_id, 'text': message}
                    
                    if self.bot_token:
                        while True:
                            try: 
                                rq.post(url, data=data)
                            except: 
                                pass
                            else: 
                                break
        except Exception as exception:
            self.send_exception(exception)