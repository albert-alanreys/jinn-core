import numpy as np
import numba as nb

import src.core.quantklines as qk
from src.core.strategy.base_strategy import BaseStrategy
from src.core.utils.deals import create_log_entry
from src.core.utils.rounding import adjust


class DailyProfitV1(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes

    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    # direction: 0 - "all", 1 — "longs", 2 — "shorts"
    # order_size_type: 0 — "PERCENT", 1 — "CURRENCY"

    params = {
        "margin_type": 0,
        "direction": 0,
        "initial_capital": 10000.0,
        "min_capital": 100.0,
        "commission": 0.075,
        "order_size_type": 0,
        "order_size": 100,
        "leverage": 1,
        "stop": 0.5,
        "trail_stop": True,
        "take_multiplier_1": 3.0,
        "take_volume_1": 30.0,
        "take_2": True,
        "take_multiplier_2": 2.0,
        "take_volume_2": 30.0,
        "st_atr_length": 14,
        "st_factor": 2.5,
        "rsi_length": 10,
        "stoch_length": 10,
        "stoch_rsi_upper_limit": 90.0,
        "stoch_rsi_lower_limit": 10.0,
        "vwap_close": True,
        "vwap_zone": 0.3
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop': [0.3, 0.5, 0.7],
        'trail_stop': [True, False],
        'take_multiplier_1': [2.0, 3.0, 4.0],
        'take_volume_1': [10.0, 20.0, 30.0],
        'take_2': [True, False],
        'take_multiplier_2': [1.5, 2.0, 2.5, 3.0],
        'take_volume_2': [10.0, 20.0, 30.0] ,
        'st_atr_length': [i for i in range(10, 20)],
        'st_factor': [2.0, 2.5, 3.0],
        'rsi_length': [i for i in range(10, 20)],
        'stoch_length': [i for i in range(10, 20)],
        'stoch_rsi_upper_limit': [80.0, 90.0],
        'stoch_rsi_lower_limit': [10.0, 20.0],
        'vwap_close': [True, False],
        'vwap_zone': [0.2, 0.3, 0.4]
    }

    # For frontend
    indicator_options = {
        'SL': {'color': '#FF0000', 'lineWidth': 2},
        'TP #1': {'color': '#008000', 'lineWidth': 2},
        'TP #2': {'color': '#008000', 'lineWidth': 2},
        'ST ↑' : {'color': '#006400','lineWidth': 1},
        'ST ↓' : {'color': '#8B0000','lineWidth': 1},
        # 'VWAP': {'lineWidth': 3}
    }

    def __init__(self, client, all_params = None, opt_params = None) -> None:
        super().__init__(client, all_params, opt_params)

    def start(self, market_data) -> None:
        self.open_deals_log = np.full(5, np.nan)
        self.completed_deals_log = np.array([])
        self.position_size = np.nan
        self.entry_signal = np.nan
        self.entry_price = np.nan
        self.entry_date = np.nan
        self.deal_type = np.nan

        self.symbol = market_data['symbol']
        self.time = market_data['klines'][:, 0]
        self.open = market_data['klines'][:, 1]
        self.high = market_data['klines'][:, 2]
        self.low = market_data['klines'][:, 3]
        self.close = market_data['klines'][:, 4]
        self.volume = market_data['klines'][:, 5]
        self.p_precision = market_data['p_precision']
        self.q_precision = market_data['q_precision']

        self.equity = self.params['initial_capital']

        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.stop_moved = False

        self.take_price = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.qty_take = np.full(2, np.nan)

        self.st_upper_band, self.st_lower_band = qk.dst(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['st_factor'],
            atr_length=self.params['st_atr_length']
        )

        self.rsi_high = qk.rsi(
            source=self.high,
            length=self.params['rsi_length']
        )
        self.rsi_low = qk.rsi(
            source=self.low,
            length=self.params['rsi_length']
        )
        self.rsi_close = qk.rsi(
            source=self.close,
            length=self.params['rsi_length']
        )
        self.stoch_rsi = qk.stoch(
            source=self.rsi_close,
            high=self.rsi_high,
            low=self.rsi_low,
            length=self.params['stoch_length']
        )

        self.vwap = qk.daily_vwap_with_reset(
            time=self.time,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )

        print(self.vwap[-50:])


        self.liquidation_price = np.nan

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_close_long = False
        self.alert_close_short = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False

        # (
        #     self.completed_deals_log,
        #     self.open_deals_log,
        #     self.take_price,
        #     self.stop_price,
        #     self.alert_cancel,
        #     self.alert_open_long,
        #     self.alert_open_short,
        #     self.alert_close_long,
        #     self.alert_close_short,
        #     self.alert_long_new_take,
        #     self.alert_short_new_take
        # ) = self._calculate(
        #     self.params['direction'],
        #     self.params['initial_capital'],
        #     self.params['commission'],
        #     self.params['order_size_type'],
        #     self.params['order_size'],
        #     self.params['leverage'],
        #     self.params['stop'],
        #     self.params['take_type'],
        #     self.params['take'],
        #     self.p_precision,
        #     self.q_precision,
        #     self.time,
        #     self.open,
        #     self.high,
        #     self.low,
        #     self.close,
        #     self.equity,
        #     self.completed_deals_log,
        #     self.open_deals_log,
        #     self.deal_type,
        #     self.entry_signal,
        #     self.entry_date,
        #     self.entry_price,
        #     self.take_price,
        #     self.stop_price,
        #     self.liquidation_price,
        #     self.position_size,
        #     self.sma_long_entry,
        #     self.sma_short_entry,
        #     self.sma_long_exit,
        #     self.sma_short_exit,
        #     self.sma_small_trend,
        #     self.sma_medium_trend,
        #     self.cond_exit_long,
        #     self.cond_exit_short,
        #     self.alert_cancel,
        #     self.alert_open_long,
        #     self.alert_open_short,
        #     self.alert_close_long,
        #     self.alert_close_short,
        #     self.alert_long_new_take,
        #     self.alert_short_new_take
        # )

        self.indicators = {
            'SL': {
                'options': self.indicator_options['SL'],
                'values': self.stop_price
            },
            'TP #1': {
                'options': self.indicator_options['TP #1'],
                'values': self.take_price[0]
            },
            'TP #2': {
                'options': self.indicator_options['TP #2'],
                'values': self.take_price[1]
            },
            'ST ↑': {
                'options': self.indicator_options['ST ↑'],
                'values': self.st_upper_band
            },
            'ST ↓': {
                'options': self.indicator_options['ST ↓'],
                'values': self.st_lower_band
            }
        }

    @staticmethod
    # @nb.jit(cache=True, nopython=True, nogil=True)
    def _calculate(
        direction: int,
        initial_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop: float,
        take_type: int,
        take: float,
        p_precision: float,
        q_precision: float,
        time: np.ndarray,
        open: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        equity: float,
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray,
        deal_type: float,
        entry_signal: float,
        entry_date: float,
        entry_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        liquidation_price: float,
        position_size: float,
        sma_long_entry: np.ndarray,
        sma_short_entry: np.ndarray,
        sma_long_exit: np.ndarray,
        sma_short_exit: np.ndarray,
        sma_small_trend: np.ndarray,
        sma_medium_trend: np.ndarray,
        cond_exit_long: np.ndarray,
        cond_exit_short: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_close_long: bool,
        alert_close_short: bool,
        alert_long_new_take: bool,
        alert_short_new_take: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_price[i] = take_price[i - 1]

            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_close_long = False
            alert_close_short = False
            alert_long_new_take = False
            alert_short_new_take = False

            # Check of liquidation
            if (deal_type == 0 and low[i] <= liquidation_price):
                log_entry = create_log_entry(
                    completed_deals_log,
                    commission,
                    deal_type,
                    entry_signal,
                    700,
                    entry_date,
                    time[i],
                    entry_price,
                    liquidation_price,
                    position_size,
                    initial_capital
                )
                completed_deals_log = np.concatenate(
                    (completed_deals_log, log_entry)
                )
                equity += log_entry[8]
                
                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                alert_cancel = True

            if (deal_type == 1 and high[i] >= liquidation_price):
                log_entry = create_log_entry(
                    completed_deals_log,
                    commission,
                    deal_type,
                    entry_signal,
                    800,
                    entry_date,
                    time[i],
                    entry_price,
                    liquidation_price,
                    position_size,
                    initial_capital
                )
                completed_deals_log = np.concatenate(
                    (completed_deals_log, log_entry)
                )
                equity += log_entry[8]

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                alert_cancel = True

            # Trading logic (longs)
            is_new_take_price = (
                take_type == 1 and
                deal_type == 0 and
                not np.isnan(take_price[i - 1])
            )

            if is_new_take_price:
                take_price[i] = min(sma_long_exit[i], take_price[i - 1])
                alert_long_new_take = True

            if deal_type == 0:
                if low[i] <= stop_price[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        500,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_price[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    position_size = np.nan
                    alert_cancel = True

                if high[i] >= take_price[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        300,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    position_size = np.nan
                    alert_cancel = True

            exit_long = (
                deal_type == 0 and
                cond_exit_long[i]
            )
            entry_long = (
                np.isnan(deal_type) and
                high[i - 1] >= sma_long_entry[i - 1] and
                low[i - 1] <= sma_long_entry[i - 1] and
                close[i] > close[i - 1] and
                close[i] > open[i] and
                close[i] > sma_small_trend[i] and
                close[i] > sma_medium_trend[i] and
                close[i] < sma_long_exit[i] and
                (direction == 0 or direction == 1)
            )

            if exit_long:
                log_entry = create_log_entry(
                    completed_deals_log,
                    commission,
                    deal_type,
                    entry_signal,
                    100,
                    entry_date,
                    time[i],
                    entry_price,
                    close[i],
                    position_size,
                    initial_capital
                )
                completed_deals_log = np.concatenate(
                    (completed_deals_log, log_entry)
                )
                equity += log_entry[8]

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                alert_close_long = True
                alert_cancel = True

            if entry_long:
                deal_type = 0
                entry_signal = 100
                entry_date = time[i]
                entry_price = close[i]

                if order_size_type == 0:
                    initial_position =  (
                        equity * leverage * (order_size / 100.0)
                    )
                    position_size = adjust(
                        initial_position * (1 - commission / 100)
                        / entry_price, q_precision
                    )
                else:
                    initial_position = (
                        order_size * leverage
                    )
                    position_size = adjust(
                        initial_position * (1 - commission / 100)
                        / entry_price, q_precision
                    )

                take_price[i] = adjust(
                    entry_price * (100 + take) / 100, p_precision
                )
                stop_price[i] = adjust(
                    entry_price * (100 - stop) / 100, p_precision
                )
                liquidation_price = adjust(
                    entry_price * (1 - (1 / leverage)), p_precision
                )

                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_open_long = True

            # Trading logic (shorts)
            is_new_take_price = (
                take_type == 1 and
                deal_type == 1 and
                not np.isnan(take_price[i - 1])
            )

            if is_new_take_price:
                take_price[i] = max(sma_short_exit[i], take_price[i - 1])
                alert_short_new_take = True

            if deal_type == 1:
                if high[i] >= stop_price[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        600,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_price[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    position_size = np.nan
                    alert_cancel = True 

                if low[i] <= take_price[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        400,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    position_size = np.nan
                    alert_cancel = True 

            exit_short = (
                deal_type == 1 and
                cond_exit_short[i]
            )
            entry_short = (
                np.isnan(deal_type) and
                high[i - 1] >= sma_short_entry[i - 1] and
                low[i - 1] <= sma_short_entry[i - 1] and
                close[i] < close[i - 1] and
                close[i] < open[i] and
                close[i] < sma_small_trend[i] and
                close[i] < sma_medium_trend[i] and
                close[i] > sma_short_exit[i] and
                (direction == 0 or direction == 2)
            )

            if exit_short:
                log_entry = create_log_entry(
                    completed_deals_log,
                    commission,
                    deal_type,
                    entry_signal,
                    200,
                    entry_date,
                    time[i],
                    entry_price,
                    close[i],
                    position_size,
                    initial_capital
                )
                completed_deals_log = np.concatenate(
                    (completed_deals_log, log_entry)
                )
                equity += log_entry[8]

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                alert_close_short = True
                alert_cancel = True

            if entry_short:
                deal_type = 1
                entry_signal = 200
                entry_date = time[i]
                entry_price = close[i]

                if order_size_type == 0:
                    initial_position = (
                        equity * leverage * (order_size / 100.0)
                    )
                    position_size = adjust(
                        initial_position * (1 - commission / 100)
                        / entry_price, q_precision
                    )
                else:
                    initial_position = (
                        order_size * leverage
                    )
                    position_size = adjust(
                        initial_position * (1 - commission / 100)
                        / entry_price, q_precision
                    )

                take_price[i] = adjust(
                    entry_price * (100 - take) / 100, p_precision
                )
                stop_price[i] = adjust(
                    entry_price * (100 + stop) / 100, p_precision
                )
                liquidation_price = adjust(
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_open_short = True

        return (
            completed_deals_log,
            open_deals_log,
            take_price,
            stop_price,
            alert_cancel,
            alert_open_long,
            alert_open_short,
            alert_close_long,
            alert_close_short,
            alert_long_new_take,
            alert_short_new_take
        )

    def trade(self) -> None:
        if self.order_ids is None:
            self.order_ids = self.cache.load(self.symbol)

        if self.alert_cancel:
            self.client.cancel_all_orders(self.symbol)

        self.order_ids['stop_ids'] = self.client.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )
        self.order_ids['limit_ids'] = self.client.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_long_new_take:
            self.client.cancel_limit_orders(
                symbol=self.symbol,
                side='Sell'
            )
            self.order_ids['limit_ids'] = self.client.check_limit_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['limit_ids']
            )
            order_id = self.client.limit_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.take_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_short_new_take:
            self.client.cancel_limit_orders(
                symbol=self.symbol,
                side='Buy'
            )
            self.order_ids['limit_ids'] = self.client.check_limit_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['limit_ids']
            )
            order_id = self.client.limit_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.take_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_close_long:
            self.client.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_close_short:
            self.client.market_close_short(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_open_long:
            self.client.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size']}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = self.client.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_short:
            self.client.market_open_short(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size']}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = self.client.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        self.cache.save(self.symbol, self.order_ids)