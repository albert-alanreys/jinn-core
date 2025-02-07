import logging
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from binance.um_futures import UMFutures

import config
import src.model.enums as enums
from src.model.api_clients.telegram_client import TelegramClient


class BinanceClient():
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

    def __init__(self) -> None:
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET

        self.alerts = []

        self.telegram_client = TelegramClient()
        self.logger = logging.getLogger(__name__)

        try:
            self.client = UMFutures(key=self.api_key, secret=self.api_secret)
        except requests.exceptions.ConnectTimeout as e:
            self.logger.error(f'Error: {e}')

    def get_valid_interval(self, interval: str | int) -> str | None:
        if interval in self.intervals:
            return self.intervals[interval]
        
        self.logger.error(f'Invalid interval: {interval}')

    def fetch_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: str,
        start: str,
        end: str
    ) -> list:
        def fetch_klines(start_range: int, end_range: int) -> list:
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_range,
                'endTime': end_range,
                'limit': 1000,
            }

            for _ in range(3):
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.Timeout:
                    time.sleep(1.0)
                except Exception:
                    pass

            return []

        match market:
            case enums.Market.SPOT:
                url = 'https://data-api.binance.vision/api/v3/klines'
            case enums.Market.FUTURES:
                url = 'https://fapi.binance.com/fapi/v1/klines'

        self.logger.info(
            f'Fetching data: BINANCE • {market.value} • '
            f'{symbol} • {interval} • {start} - {end}'
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

        with ThreadPoolExecutor(max_workers=7) as executor:
            results = executor.map(lambda t: fetch_klines(*t), time_ranges)

            for result in results:
                klines.extend(result)

        return klines

    def fetch_last_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000
    ) -> list:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit,
        }

        for _ in range(3):
            try:
                response = requests.get(
                    url='https://fapi.binance.com/fapi/v1/klines',
                    params=params
                )
                response.raise_for_status()
                return response.json()[:-1]
            except requests.exceptions.Timeout:
                time.sleep(1.0)
            except Exception:
                pass

        return []

    def fetch_price_precision(self, symbol: str) -> float:
        url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
        params = {'symbol': symbol}

        for _ in range(3):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                symbols_info = response.json()['symbols']
                symbol_info = next(
                    filter(lambda x: x['symbol'] == symbol, symbols_info)
                )
                return float(symbol_info['filters'][0]['tickSize'])
            except requests.exceptions.Timeout:
                time.sleep(1.0)
            except Exception:
                pass

        return 1.0

    def fetch_qty_precision(self, symbol: str) -> float:
        url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
        params = {'symbol': symbol}

        for _ in range(3):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                symbols_info = response.json()['symbols']
                symbol_info = next(
                    filter(lambda x: x['symbol'] == symbol, symbols_info)
                )
                return float(symbol_info['filters'][1]['stepSize'])
            except requests.exceptions.Timeout:
                time.sleep(1.0)
            except Exception:
                pass

        return 1.0

    def futures_market_open_buy(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: str
    ) -> None:
        if hedge == 'false':
            hedge_mode = 'BOTH'

            try:
                self.client.change_position_mode(dualSidePosition=False)
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 'LONG'

            try:
                self.client.change_position_mode(dualSidePosition=True)
            except Exception:
                pass

        try:
            if margin == 'cross':
                self.client.change_margin_type(
                    symbol=symbol,
                    marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.client.change_margin_type(
                    symbol=symbol,
                    marginType='ISOLATED'
                )
        except Exception:
            pass

        try:
            self.client.change_leverage(
                symbol=symbol,
                leverage=leverage
            )
        except Exception:
            pass

        try:
            market_price = float(
                self.client.mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.client.account()['assets']
            balance = float(
                next(
                    filter(lambda x: x['asset'] == 'USDT', balance_info)
                )['availableBalance']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            qty_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / qty_precision) * qty_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty
            )

            for _ in range(3):
                try:
                    order_info = self.client.query_order(
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
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_open_sell(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: int,
        hedge: str
    ) -> None:
        if hedge == 'false':
            hedge_mode = 'BOTH'

            try:
                self.client.change_position_mode(dualSidePosition=False)
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 'SHORT'

            try:
                self.client.change_position_mode(dualSidePosition=True)
            except Exception:
                pass

        try:
            if margin == 'cross':
                self.client.change_margin_type(
                    symbol=symbol,
                    marginType='CROSSED'
                )
            elif margin == 'isolated':
                self.client.change_margin_type(
                    symbol=symbol,
                    marginType='ISOLATED'
                )
        except Exception:
            pass

        try:
            self.client.change_leverage(
                symbol=symbol,
                leverage=leverage
            )
        except Exception:
            pass

        try:
            market_price = float(
                self.client.mark_price(symbol=symbol)['markPrice']
            )
            balance_info = self.client.account()['assets']
            balance = float(
                next(
                    filter(lambda x: x['asset'] == 'USDT', balance_info)
                )['availableBalance']
            )

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty
            )

            for _ in range(3):
                try:
                    order_info = self.client.query_order(
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
            self.telegram_client.send_message(message)
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

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            for _ in range(3):
                try:
                    order_info = self.client.query_order(
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
            self.telegram_client.send_message(message)
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

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='MARKET',
                quantity=qty,
                reduceOnly=reduce_only
            )

            for _ in range(3):
                try:
                    order_info = self.client.query_order(
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
            self.telegram_client.send_message(message)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_stop_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> int | None:
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='STOP_MARKET',
                quantity=qty,
                stopPrice=price,
                reduceOnly=reduce_only
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
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> int | None:
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='STOP_MARKET',
                quantity=qty,
                stopPrice=price,
                reduceOnly=reduce_only
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
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> int | None:
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'SHORT'

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='BUY',
                positionSide=hedge_mode,
                type='LIMIT',
                timeInForce='GTC',
                quantity=qty,
                price=price,
                reduceOnly=reduce_only
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
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> int | None:
        try:
            if hedge == 'false':
                reduce_only = True
                hedge_mode = 'BOTH'
            elif hedge == 'true':
                reduce_only = None
                hedge_mode = 'LONG'

            positions_info = self.client.get_position_risk(symbol=symbol)
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
                    self.client.mark_price(symbol=symbol)['markPrice']
                )
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.new_order(
                symbol=symbol,
                side='SELL',
                positionSide=hedge_mode,
                type='LIMIT',
                timeInForce='GTC',
                quantity=qty,
                price=price,
                reduceOnly=reduce_only
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
            self.telegram_client.send_message(message)
            return order['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self.client.get_orders(symbol=symbol)
            stop_orders = list(
                filter(
                    lambda x: x['type'] == 'STOP_MARKET' and
                        x['side'] == side.upper(),
                    orders_info
                )
            )

            for order in stop_orders:
                self.client.cancel_order(
                    symbol=symbol,
                    orderId=order['orderId']
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
            orders_info = self.client.get_orders(symbol=symbol)
            one_sided_orders = list(
                filter(
                    lambda x: x['side'] == side.upper(), orders_info
                )
            )

            for order in one_sided_orders:
                self.client.cancel_order(
                    symbol=symbol,
                    orderId=order['orderId']
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.client.cancel_open_orders(symbol)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_stop_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                orders_info = self.client.get_all_orders(
                    symbol=symbol,
                    orderId=order_id
                )
                order_info = next(
                    filter(lambda x: x['orderId'] == order_id, orders_info)
                )

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
                        order_info['updateTime'] / 1000, tz=timezone.utc
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
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_limit_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                orders_info = self.client.get_all_orders(
                    symbol=symbol,
                    orderId=order_id
                )
                order_info = next(
                    filter(lambda x: x['orderId'] == order_id, orders_info)
                )

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
                        order_info['updateTime'] / 1000, tz=timezone.utc
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
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def send_exception(self, exception: Exception) -> None:
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