import requests as rq
import datetime as dt
import abc
import os
from typing import Callable

import numpy as np


class Client(abc.ABC):
    def __init__(
            self,
            intervals: dict[str | int, str | int],
            exchange: str,
        ) -> None:
        self.exchange = exchange.upper()
        self.intervals = intervals

        with open(os.path.abspath('.env'), 'r') as file:
            for line in file.readlines():
                if line.startswith(chars := f'{self.exchange}_API_KEY='):
                    self.api_key = (
                        line.lstrip(chars).rstrip('\n')
                    )

                if line.startswith(chars := f'{self.exchange}_API_SECRET='):
                    self.api_secret = (
                        line.lstrip(chars).rstrip('\n')
                    )

                if line.startswith(chars := 'TELEGRAM_BOT_TOKEN='):
                    self.bot_token = (
                        line.lstrip(chars).rstrip('\n')
                    )

                if line.startswith(chars := 'TELEGRAM_CHAT_ID='):
                    self.chat_id = (
                        line.lstrip(chars).rstrip('\n')
                    )

        self.telegram_url = (
            f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        )
        self.limit_orders = []
        self.stop_orders = []
        self.alerts = []

    def create_session(
        self,
        callback: Callable,
        testnet: bool
    ) -> None:
        self.session = callback(
            testnet=testnet,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

    def send_exception(
        self,
        exception: Exception
    ) -> None:
        if str(exception) != '':
            self.alerts.append({
                'message': {
                    'exchange': self.exchange.upper(),
                    'error': str(exception)
                },
                'time': dt.datetime.now(
                    dt.timezone.utc
                ).strftime('%Y-%m-%d %H:%M:%S')
            })
            message = f'❗️{self.exchange}:\n{exception}'
            self.send_message(message)

    def send_message(self, message: str) -> None:
        try:
            if self.bot_token:
                rq.post(
                    self.telegram_url,
                    {'chat_id': self.chat_id, 'text': message}
                )
        except Exception:
            pass

    def get_data(
        self,
        symbol: str,
        interval: str | int,
        start_time: str | None = None,
        end_time: str | None = None
    ) -> None:
        interval = self.intervals[interval]

        if start_time and end_time:
            self.get_data_from_database(
                symbol, interval, start_time, end_time
            )
        else:
            self.get_last_klines(symbol, interval)

        self.price_precision = self.get_price_precision(symbol)
        self.qty_precision = self.get_qty_precision(symbol)
    
    def get_data_from_database(
        self,
        symbol: str,
        interval: str | int,
        start_time: str,
        end_time: str
    ) -> None:
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
        file = (
            f'{os.path.abspath('src/database')}'
            f'/{self.exchange.lower()}_{symbol}_{interval}_'
            f'{start_time}_{end_time}.npy'
        )

        try:
            self.price_data = np.load(file)
        except FileNotFoundError:
            self.get_historical_klines(
                symbol, interval, start_time, end_time
            )
            np.save(file, self.price_data)

    @abc.abstractmethod
    def get_historical_klines(
        self,
        symbol: str,
        interval: int | str,
        start_time: int,
        end_time: int
    ) -> None:
        pass

    @abc.abstractmethod
    def get_last_klines(
        self,
        symbol: str,
        interval: int | str
    ) -> None:
        pass

    @abc.abstractmethod
    def get_price_precision(self, symbol: str) -> float:
        pass

    @abc.abstractmethod
    def get_qty_precision(self, symbol: str) -> float:
        pass

    @abc.abstractmethod
    def update_data(self) -> bool | None:
        pass

    @abc.abstractmethod
    def futures_market_open_buy(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: str,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_market_open_sell(
        self,
        symbol: str,
        size: str,
        margin: str,
        leverage: str,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_market_close_buy(
        self,
        symbol: str,
        size: str,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_market_close_sell(
        self,
        symbol: str,
        size: str,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_market_stop_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_market_stop_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_limit_take_buy(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_limit_take_sell(
        self,
        symbol: str,
        size: str,
        price: float,
        hedge: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_cancel_stop(
        self,
        symbol: str,
        side: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_cancel_one_sided_orders(
        self,
        symbol: str,
        side: str
    ) -> None:
        pass

    @abc.abstractmethod
    def futures_cancel_all_orders(self, symbol: str) -> None:
        pass

    @abc.abstractmethod
    def check_stop_status(self, symbol: str) -> None:
        pass

    @abc.abstractmethod
    def check_limit_status(self, symbol: str) -> None:
        pass