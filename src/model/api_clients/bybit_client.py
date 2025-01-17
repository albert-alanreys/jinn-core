import logging
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from pybit.unified_trading import HTTP

import config
import src.model.enums as enums
from src.model.api_clients.telegram_client import TelegramClient


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

        self.alerts = []

        self.telegram_client = TelegramClient()
        self.logger = logging.getLogger(__name__)

        try:
            self.client = HTTP(
                testnet=False,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
        except requests.exceptions.ConnectTimeout as e:
            self.logger.error(f'Error: {e}')

    def fetch_historical_klines(
        self,
        symbol: str,
        market: enums.Market,
        interval: enums.BybitInterval,
        start: str,
        end: str
    ) -> list:
        if isinstance(interval, enums.BinanceInterval):
            self.logger.error(f'Invalid interval: {interval}')
            return []

        def fetch_klines(start_range: int, end_range: int) -> list:
            for _ in range(3):
                try:
                    klines = self.client.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval.value,
                        start=start_range,
                        end=end_range,
                        limit=1000
                    )['result']['list'][::-1]
                    return klines
                except requests.exceptions.Timeout:
                    time.sleep(1.0)
                except Exception:
                    pass

            return []

        match market:
            case enums.Market.SPOT:
                category = 'spot'
            case enums.Market.FUTURES:
                category = 'linear'

        self.logger.info(
            f'Fetching data: BYBIT • {symbol} • {market.value} • '
            f'{interval.value} • {start} - {end}'
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
        interval: enums.BybitInterval | int | str,
        limit: int = 1000
    ) -> list:
            if isinstance(interval, enums.BinanceInterval):
                self.logger.error(f'Invalid interval: {interval}')
                return []
            
            if isinstance(interval, enums.BybitInterval):
                interval = interval.value

            for _ in range(3):
                try:
                    klines = self.client.get_kline(
                        category='linear',
                        symbol=symbol,
                        interval=interval,
                        limit=limit
                    )['result']['list'][:0:-1]
                    return klines
                except requests.exceptions.Timeout:
                    time.sleep(1.0)
                except Exception:
                    pass

            return []

    def fetch_price_precision(self, symbol: str) -> float:
        for _ in range(3):
            try:
                symbol_info = self.client.get_instruments_info(
                    category="linear", symbol=symbol
                )['result']['list'][0]
                return float(symbol_info['priceFilter']['tickSize'])
            except requests.exceptions.Timeout:
                time.sleep(1.0)
            except Exception:
                pass

        return 1.0

    def fetch_qty_precision(self, symbol: str) -> float:
        for _ in range(3):
            try:
                symbol_info = self.client.get_instruments_info(
                    category="linear", symbol=symbol
                )['result']['list'][0]
                return float(symbol_info['lotSizeFilter']['qtyStep'])
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
            hedge_mode = 0

            try:
                self.client.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=0,
                )
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 1

            try:
                self.client.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception:
                pass

        try:
            if margin == 'cross':
                self.client.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=0,
                    buyLeverage='1',
                    sellLeverage='1',
                )
            elif margin == 'isolated':
                self.client.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=1,
                    buyLeverage='1',
                    sellLeverage='1',
                )
        except Exception:
            pass

        try:
            self.client.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage),
            )
        except Exception:
            pass

        try:
            market_price = float(self.client.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])
            balance = float(self.client.get_wallet_balance(
                accountType='UNIFIED', coin='USDT',
            )['result']['list'][0]['coin'][0]['availableToWithdraw'])

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
            hedge_mode = 0

            try:
                self.client.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=0,
                )
            except Exception:
                pass
        elif hedge == 'true':
            hedge_mode = 2

            try:
                self.client.switch_position_mode(
                    category='linear',
                    symbol=symbol,
                    mode=3,
                )
            except Exception:
                pass

        try:
            if margin == 'cross':
                self.client.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=0,
                    buyLeverage='1',
                    sellLeverage='1',
                )
            elif margin == 'isolated':
                self.client.switch_margin_mode(
                    category='linear',
                    symbol=symbol,
                    tradeMode=1,
                    buyLeverage='1',
                    sellLeverage='1',
                )
        except Exception:
            pass

        try:
            self.client.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage),
            )
        except Exception:
            pass

        try:
            market_price = float(self.client.get_tickers(
                category='linear', symbol=symbol
            )['result']['list'][0]['lastPrice'])
            balance = float(self.client.get_wallet_balance(
                accountType='UNIFIED', coin='USDT',
            )['result']['list'][0]['coin'][0]['availableToWithdraw'])

            if size.endswith('%'):
                size = float(size.rstrip('%'))
                qty = balance * leverage * size * 0.01 / market_price
            elif size.endswith('u'):
                size = float(size.rstrip('u'))
                qty = leverage * size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.client.get_positions(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.client.get_positions(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Market',
                qty=qty,
                positionIdx=hedge_mode
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
    ) -> str | None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.client.get_positions(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.place_order(
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

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> str | None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.client.get_positions(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.place_order(
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

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> str | None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 2

            positions_info = self.client.get_positions(
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
                    orders_info = self.client.get_open_orders(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Buy',
                orderType='Limit',
                qty=qty,
                price=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> str | None:
        try:
            if hedge == 'false':
                hedge_mode = 0
            elif hedge == 'true':
                hedge_mode = 1

            positions_info = self.client.get_positions(
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
                    orders_info = self.client.get_open_orders(
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
                market_price = float(self.client.get_tickers(
                    category='linear', symbol=symbol
                )['result']['list'][0]['lastPrice'])
                qty = size / market_price

            q_precision = self.fetch_qty_precision(symbol)
            p_precision = self.fetch_price_precision(symbol)
            qty = round(round(qty / q_precision) * q_precision, 8)
            price = round(round(price / p_precision) * p_precision, 8)

            order = self.client.place_order(
                category='linear',
                symbol=symbol,
                side='Sell',
                orderType='Limit',
                qty=qty,
                price=price,
                positionIdx=hedge_mode,
                reduceOnly=True
            )

            for _ in range(3):
                try:
                    order_info = self.client.get_open_orders(
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
            self.telegram_client.send_message(message)
            return order['result']['orderId']
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
        try:
            orders_info = self.client.get_open_orders(
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
                self.client.cancel_order(
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
            orders_info = self.client.get_open_orders(
                category='linear', symbol=symbol
            )['result']['list']
            one_sided_orders = list(
                filter(lambda x: x['side'] == side, orders_info)
            )

            for i in one_sided_orders:
                self.client.cancel_order(
                    category='linear',
                    symbol=symbol,
                    orderId=i['orderId']
                )
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def futures_cancel_all_orders(self, symbol: str) -> None:
        try:
            self.client.cancel_all_orders(category='linear', symbol=symbol)
        except Exception as e:
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_stop_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                order = self.client.get_open_orders(
                    category="linear",
                    symbol=symbol,
                    orderId=order_id
                )
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
                        tz=timezone.utc
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
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def check_limit_orders(self, symbol: str, order_ids: list) -> list | None:
        try:
            for order_id in order_ids.copy():
                order = self.client.get_open_orders(
                    category="linear",
                    symbol=symbol,
                    orderId=order_id
                )
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
                        tz=timezone.utc
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
            self.logger.error(f'Error: {e}')
            self.send_exception(e)

    def send_exception(self, exception: Exception) -> None:
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