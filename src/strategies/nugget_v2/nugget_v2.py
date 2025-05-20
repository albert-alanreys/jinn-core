from random import randint

import numpy as np
import numba as nb

import src.core.lib.ta as ta
from src.core.strategy.base_strategy import BaseStrategy


class NuggetV2(BaseStrategy):
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
        "stop_type": 1,
        "stop": 2.8,
        "trail_stop": 1,
        "trail_percent": 30.0,
        "take_percent": [4.5, 5.9, 12.8, 19.5, 27.8],
        "take_volume": [10.0, 10.0, 50.0, 20.0, 10.0],
        "st_atr_period": 6,
        "st_factor": 24.6,
        "st_upper_band": 5.8,
        "st_lower_band": 2.9,
        "rsi_length": 6,
        "rsi_long_upper_limit": 29.0,
        "rsi_long_lower_limit": 28.0,
        "rsi_short_upper_limit": 69.0,
        "rsi_short_lower_limit": 58.0,
        "bb_filter": False,
        "ma_length": 22,
        "bb_mult": 2.7,
        "bb_long_limit": 24.0,
        "bb_short_limit": 67.0,
        "adx_filter": False,
        "adx_length": 6,
        "di_length": 14,
        "adx_long_upper_limit": 44.0,
        "adx_long_lower_limit": 28.0,
        "adx_short_upper_limit": 77.0,
        "adx_short_lower_limit": 1.0
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_type': [i for i in range(1, 3)],
        'stop': [i / 10 for i in range(1, 31)],
        'trail_stop': [i for i in range(1, 4)],
        'trail_percent': [float(i) for i in range(0, 55, 1)],
        'take_percent': [
            [
                randint(12, 46) / 10,
                randint(48, 86) / 10,
                randint(88, 146) / 10,
                randint(148, 196) / 10,
                randint(198, 326) / 10
            ] for _ in range(100)
        ],
        'take_volume': [
            [20.0, 20.0, 20.0, 20.0, 20.0],
            [40.0, 30.0, 15.0, 10.0, 5.0],
            [5.0, 10.0, 15.0, 30.0, 40.0],
            [10.0, 20.0, 30.0, 20.0, 20.0],
            [25.0, 25.0, 25.0, 15.0, 10.0],
            [15.0, 15.0, 30.0, 30.0, 10.0],
            [50.0, 20.0, 10.0, 10.0, 10.0],
            [10.0, 10.0, 10.0, 20.0, 50.0],
            [30.0, 20.0, 20.0, 20.0, 10.0],
            [10.0, 20.0, 20.0, 20.0, 30.0],
            [35.0, 25.0, 15.0, 15.0, 10.0],
            [10.0, 15.0, 15.0, 25.0, 35.0],
            [25.0, 15.0, 25.0, 15.0, 20.0],
            [10.0, 30.0, 10.0, 30.0, 20.0],
            [45.0, 15.0, 15.0, 15.0, 10.0],
            [10.0, 15.0, 15.0, 15.0, 45.0],
            [15.0, 25.0, 15.0, 25.0, 20.0],
            [33.0, 22.0, 11.0, 22.0, 12.0],
            [12.5, 25.0, 25.0, 25.0, 12.5],
            [5.0, 15.0, 30.0, 30.0, 20.0]
        ],
        'st_atr_period': [i for i in range(2, 21)],
        'st_factor': [i / 100 for i in range(1000, 2501, 5)],
        'st_upper_band': [i / 10 for i in range(39, 69)],
        'st_lower_band': [i / 10 for i in range(11, 37)],
        'rsi_length': [i for i in range(3, 22)],
        'rsi_long_upper_limit': [float(i) for i in range(29, 51)],
        'rsi_long_lower_limit': [float(i) for i in range(1, 29)],
        'rsi_short_upper_limit': [float(i) for i in range(69, 101)],
        'rsi_short_lower_limit': [float(i) for i in range(50, 69)],
        'bb_filter': [True, False],
        'ma_length': [i for i in range(3, 26)],
        'bb_mult': [i / 10 for i in range(11, 31)],
        'bb_long_limit': [float(i) for i in range(20, 51)],
        'bb_short_limit': [float(i) for i in range(50, 81)],
        'adx_filter': [False, True],
        'adx_length': [i for i in range(1, 21)],
        'di_length': [i for i in range(1, 21)],
        'adx_long_upper_limit': [float(i) for i in range(29, 51)],
        'adx_long_lower_limit': [float(i) for i in range(1, 29)],
        'adx_short_upper_limit': [float(i) for i in range(69, 101)],
        'adx_short_lower_limit': [float(i) for i in range(1, 69)]
    }

    # For frontend
    indicator_options = {
        'SL': {'color': '#FF0000'},
        'TP #1': {'color': '#008000'},
        'TP #2': {'color': '#008000'},
        'TP #3': {'color': '#008000'},
        'TP #4': {'color': '#008000'},
        'TP #5': {'color': '#008000'}
    }

    def __init__(self, client, all_params = None, opt_params = None) -> None:
        super().__init__(client, all_params=all_params, opt_params=opt_params)

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
        self.high = market_data['klines'][:, 2]
        self.low = market_data['klines'][:, 3]
        self.close = market_data['klines'][:, 4]
        self.p_precision = market_data['p_precision']
        self.q_precision = market_data['q_precision']

        self.equity = self.params['initial_capital']
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.liquidation_price = np.nan
        self.qty_take = np.full(5, np.nan)
        self.stop_moved = False

        self.ds = ta.ds(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['st_factor'],
            atr_length=self.params['st_atr_period']
        )
        self.change_upper_band = ta.change(source=self.ds[0], length=1)
        self.change_lower_band = ta.change(source=self.ds[1], length=1)
        self.rsi = ta.rsi(source=self.close, length=self.params['rsi_length'])

        if self.params['bb_filter']:
            self.bb_rsi = ta.bb(
                source=self.rsi,
                length=self.params['ma_length'],
                mult=self.params['bb_mult']
            )
        else:
            self.bb_rsi = np.full(self.time.shape[0], np.nan)

        if self.params['adx_filter']:
            dmi = ta.dmi(
                high=self.high,
                low=self.low,
                close=self.close,
                di_length=self.params['di_length'],
                adx_length=self.params['adx_length']
            )
            self.adx = dmi[2]
        else:
            self.adx = np.full(self.time.shape[0], np.nan)

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.take_price,
            self.stop_price,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_long_new_stop,
            self.alert_short_new_stop
        ) = self._calculate(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['min_capital'],
            self.params['commission'],
            self.params['order_size_type'],
            self.params['order_size'],
            self.params['leverage'],
            self.params['stop_type'],
            self.params['stop'],
            self.params['trail_stop'],
            self.params['trail_percent'],
            self.params['take_percent'],
            self.params['take_volume'],
            self.params['st_upper_band'],
            self.params['st_lower_band'],
            self.params['rsi_long_upper_limit'],
            self.params['rsi_long_lower_limit'],
            self.params['rsi_short_upper_limit'],
            self.params['rsi_short_lower_limit'],
            self.params['bb_filter'],
            self.params['bb_long_limit'],
            self.params['bb_short_limit'],
            self.params['adx_filter'],
            self.params['adx_long_upper_limit'],
            self.params['adx_long_lower_limit'],
            self.params['adx_short_upper_limit'],
            self.params['adx_short_lower_limit'],
            self.p_precision,
            self.q_precision,
            self.time,
            self.high,
            self.low,
            self.close,
            self.equity,
            self.completed_deals_log,
            self.open_deals_log,
            self.deal_type,
            self.entry_signal,
            self.entry_date,
            self.entry_price,
            self.liquidation_price,
            self.take_price,
            self.stop_price,
            self.position_size,
            self.qty_take,
            self.stop_moved,
            self.ds[0],
            self.ds[1],
            self.change_upper_band,
            self.change_lower_band,
            self.rsi,
            self.bb_rsi[1] if self.params['bb_filter'] else self.bb_rsi,
            self.bb_rsi[2] if self.params['bb_filter'] else self.bb_rsi,
            self.adx,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_long_new_stop,
            self.alert_short_new_stop
        )

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
            'TP #3': {
                'options': self.indicator_options['TP #3'],
                'values': self.take_price[2]
            },
            'TP #4': {
                'options': self.indicator_options['TP #4'],
                'values': self.take_price[3]
            },
            'TP #5': {
                'options': self.indicator_options['TP #5'],
                'values': self.take_price[4]
            }
        }

    @staticmethod
    @nb.jit(cache=True, nopython=True, nogil=True)
    def _calculate(
        direction: int,
        initial_capital: float,
        min_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop_type: int,
        stop: float,
        trail_stop: int,
        trail_percent: float,
        take_percent: list,
        take_volume: list,
        st_upper_band: float,
        st_lower_band: float,
        rsi_long_upper_limit: float,
        rsi_long_lower_limit: float,
        rsi_short_upper_limit: float,
        rsi_short_lower_limit: float,
        bb_filter: bool,
        bb_long_limit: float,
        bb_short_limit: float,
        adx_filter: bool,
        adx_long_upper_limit: float,
        adx_long_lower_limit: float,
        adx_short_upper_limit: float,
        adx_short_lower_limit: float,
        p_precision: float,
        q_precision: float,
        time: np.ndarray,
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
        liquidation_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        position_size: float,
        qty_take: np.ndarray,
        stop_moved: int,
        ds_upper_band: np.ndarray,
        ds_lower_band: np.ndarray,
        change_upper_band: np.ndarray,
        change_lower_band: np.ndarray,
        rsi: np.ndarray,
        bb_rsi_upper: np.ndarray,
        bb_rsi_lower: np.ndarray,
        adx: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_long_new_stop: bool,
        alert_short_new_stop: bool
    ) -> tuple:
        def adjust(number: float, precision: float, digits: int = 8) -> float:
            return round(round(number / precision) * precision, digits)

        def update_log(
            log: np.ndarray,
            equity: float,
            commission: float,
            deal_type: float,
            entry_signal: float,
            exit_signal: float,
            entry_date: float,
            exit_date: float,
            entry_price: float,
            exit_price: float,
            position_size: float,
            initial_capital: float
        ) -> tuple[np.ndarray, float]:
            total_commission = round(
                (position_size * entry_price
                    * commission / 100) + (position_size
                    * exit_price * commission / 100),
                2
            )

            if deal_type == 0:
                pnl = round(
                    (exit_price - entry_price) * position_size
                        - total_commission,
                    2
                )
            else:
                pnl = round(
                    (entry_price - exit_price) * position_size
                        - total_commission,
                    2
                )

            if position_size == 0:
                return log, equity

            pnl_per = round(
                (((position_size * entry_price) + pnl)
                    / (position_size * entry_price) - 1) * 100,
                2
            )

            if log.shape[0] == 0:
                cum_pnl = round(pnl, 2)
                cum_pnl_per = round(
                    pnl / (initial_capital + pnl) * 100,
                    2
                )
            else:
                cum_pnl = round(pnl + log[-3], 2)
                cum_pnl_per = round(
                    pnl / (initial_capital + log[-3]) * 100,
                    2
                )

            log_row = np.array(
                [
                    deal_type, entry_signal, exit_signal, entry_date,
                    exit_date, entry_price, exit_price, position_size,
                    pnl, pnl_per, cum_pnl, cum_pnl_per, total_commission
                ]
            )
            log = np.concatenate((log, log_row))
            equity += pnl
            return log, equity

        for i in range(time.shape[0]):
            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_long_new_stop = False
            alert_short_new_stop = False

            if i > 0:
                stop_price[i] = stop_price[i - 1]
                take_price[:, i : i + 1] = take_price[:, i - 1 : i]

            # Check of liquidation
            if (deal_type == 0 and low[i] <= liquidation_price):
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    0,
                    entry_date,
                    time[i],
                    entry_price,
                    liquidation_price,
                    position_size,
                    initial_capital
                )
                
                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                liquidation_price = np.nan
                take_price[:, i : i + 1] = np.full(5, np.nan).reshape((5, 1))
                stop_price[i] = np.nan
                position_size = np.nan
                qty_take = np.full(5, np.nan)
                stop_moved = False
                alert_cancel = True

            if (deal_type == 1 and high[i] >= liquidation_price):
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    0,
                    entry_date,
                    time[i],
                    entry_price,
                    liquidation_price,
                    position_size,
                    initial_capital
                )

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                liquidation_price = np.nan
                take_price[:, i : i + 1] = np.full(5, np.nan).reshape((5, 1))
                stop_price[i] = np.nan
                position_size = np.nan
                qty_take = np.full(5, np.nan)
                stop_moved = False
                alert_cancel = True

            # Trading logic (longs)
            if deal_type == 0:
                if low[i] <= stop_price[i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        1,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_price[i],
                        position_size,
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    liquidation_price = np.nan
                    take_price[:, i : i + 1] = np.full(5, np.nan).reshape((5, 1))
                    stop_price[i] = np.nan
                    position_size = np.nan
                    qty_take = np.full(5, np.nan)
                    stop_moved = False
                    alert_cancel = True

                if (stop_type == 1 and
                        change_lower_band[i] and
                        ((ds_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = adjust(
                        ds_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                    alert_long_new_stop = True
                elif stop_type == 2 and not stop_moved:
                    take = None

                    if (trail_stop == 4 and
                            high[i] >= take_price[3][i]):
                        take = take_price[3][i]
                    elif (trail_stop == 3 and
                            high[i] >= take_price[2][i]):
                        take = take_price[2][i]
                    elif (trail_stop == 2 and
                            high[i] >= take_price[1][i]):
                        take = take_price[1][i]
                    elif (trail_stop == 1 and
                            high[i] >= take_price[0][i]):
                        take = take_price[0][i]

                    if take is not None:
                        stop_moved = True
                        stop_price[i] = adjust(
                            (take - entry_price) * (trail_percent / 100)
                                + entry_price,
                            p_precision
                        )
                        alert_long_new_stop = True

                if not np.isnan(take_price[0][i]) and high[i] >= take_price[0][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        2,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[0][i],
                        qty_take[0],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[0], 8)
                    open_deals_log[4] = position_size
                    take_price[0][i] = np.nan
                    qty_take[0] = np.nan

                if not np.isnan(take_price[1][i]) and high[i] >= take_price[1][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        3,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[1][i],
                        qty_take[1],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[1], 8)
                    open_deals_log[4] = position_size
                    take_price[1][i] = np.nan
                    qty_take[1] = np.nan

                if not np.isnan(take_price[2][i]) and high[i] >= take_price[2][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        4,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[2][i],
                        qty_take[2],
                        initial_capital
                    ) 

                    position_size = round(position_size - qty_take[2], 8)
                    open_deals_log[4] = position_size
                    take_price[2][i] = np.nan
                    qty_take[2] = np.nan

                if not np.isnan(take_price[3][i]) and high[i] >= take_price[3][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        5,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[3][i],
                        qty_take[3],
                        initial_capital
                    ) 

                    position_size = round(position_size - qty_take[3], 8)
                    open_deals_log[4] = position_size
                    take_price[3][i] = np.nan
                    qty_take[3] = np.nan

                if not np.isnan(take_price[4][i]) and high[i] >= take_price[4][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        6,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[4][i],
                        round(qty_take[4], 8),
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    take_price[4][i] = np.nan
                    qty_take[4] = np.nan
                    stop_price[i] = np.nan
                    stop_moved = False
                    alert_cancel = True

            entry_long = (
                (close[i] / ds_lower_band[i] - 1) * 100 > st_lower_band and
                (close[i] / ds_lower_band[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_long_upper_limit and
                rsi[i] > rsi_long_lower_limit and
                np.isnan(deal_type) and
                (bb_rsi_upper[i] < bb_long_limit
                    if bb_filter else True) and
                (adx[i] < adx_long_upper_limit and
                    adx[i] > adx_long_lower_limit
                    if adx_filter else True) and
                (equity > min_capital) and
                (direction == 0 or direction == 1)
            )

            if entry_long:
                deal_type = 0
                entry_signal = 0
                entry_price = close[i]

                if order_size_type == 0:
                    initial_position =  (
                        equity * leverage * (order_size / 100.0)
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                elif order_size_type == 1:
                    initial_position = (
                        order_size * leverage
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                    
                entry_date = time[i]
                liquidation_price = adjust(
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    ds_lower_band[i] * (100 - stop) / 100, p_precision
                )
                take_price[0][i] = adjust(
                    close[i] * (100 + take_percent[0]) / 100, p_precision
                )
                take_price[1][i] = adjust(
                    close[i] * (100 + take_percent[1]) / 100, p_precision
                )
                take_price[2][i] = adjust(
                    close[i] * (100 + take_percent[2]) / 100, p_precision
                )
                take_price[3][i] = adjust(
                    close[i] * (100 + take_percent[3]) / 100, p_precision
                )
                take_price[4][i] = adjust(
                    close[i] * (100 + take_percent[4]) / 100, p_precision
                )
                position_size = adjust(
                    position_size, q_precision
                )
                qty_take[0] = adjust(
                    position_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = adjust(
                    position_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = adjust(
                    position_size * take_volume[2] / 100, q_precision
                )
                qty_take[3] = adjust(
                    position_size * take_volume[3] / 100, q_precision
                )
                qty_take[4] = adjust(
                    position_size * take_volume[4] / 100, q_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_open_long = True

            # Trading logic (shorts)
            if deal_type == 1:
                if high[i] >= stop_price[i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        1,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_price[i],
                        position_size,
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    liquidation_price = np.nan
                    take_price[:, i : i + 1] = np.full(5, np.nan).reshape((5, 1))
                    stop_price[i] = np.nan
                    position_size = np.nan
                    qty_take = np.full(5, np.nan)
                    stop_moved = False
                    alert_cancel = True 

                if (stop_type == 1 and
                        change_upper_band[i] and
                        ((ds_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = adjust(
                        (ds_upper_band[i] * (100 + stop) / 100), 
                        p_precision
                    )
                    alert_short_new_stop = True
                elif stop_type == 2 and not stop_moved:
                    take = None

                    if (trail_stop == 4 and
                            low[i] <= take_price[3][i]):
                        take = take_price[3][i]
                    elif (trail_stop == 3 and
                            low[i] <= take_price[2][i]):
                        take = take_price[2][i]
                    elif (trail_stop == 2 and
                            low[i] <= take_price[1][i]):
                        take = take_price[1][i]
                    elif (trail_stop == 1 and
                            low[i] <= take_price[0][i]):
                        take = take_price[0][i]

                    if take is not None:
                        stop_moved = True
                        stop_price[i] = adjust(
                            (take - entry_price) * (trail_percent / 100)
                                + entry_price,
                            p_precision
                        )
                        alert_short_new_stop = True

                if not np.isnan(take_price[0][i]) and low[i] <= take_price[0][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        2,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[0][i],
                        qty_take[0],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[0], 8)
                    open_deals_log[4] = position_size
                    take_price[0][i] = np.nan
                    qty_take[0] = np.nan

                if not np.isnan(take_price[1][i]) and low[i] <= take_price[1][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        3,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[1][i],
                        qty_take[1],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[1], 8)
                    open_deals_log[4] = position_size
                    take_price[1][i] = np.nan
                    qty_take[1] = np.nan      

                if not np.isnan(take_price[2][i]) and low[i] <= take_price[2][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        4,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[2][i],
                        qty_take[2],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[2], 8)
                    open_deals_log[4] = position_size
                    take_price[2][i] = np.nan
                    qty_take[2] = np.nan

                if not np.isnan(take_price[3][i]) and low[i] <= take_price[3][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        5,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[3][i],
                        qty_take[3],
                        initial_capital
                    )

                    position_size = round(position_size - qty_take[3], 8)
                    open_deals_log[4] = position_size
                    take_price[3][i] = np.nan
                    qty_take[3] = np.nan     

                if not np.isnan(take_price[4][i]) and low[i] <= take_price[4][i]:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        6,
                        entry_date,
                        time[i],
                        entry_price,
                        take_price[4][i],
                        round(qty_take[4], 8),
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    take_price[4][i] = np.nan
                    qty_take[4] = np.nan
                    stop_price[i] = np.nan
                    stop_moved = False
                    alert_cancel = True

            entry_short = (
                (ds_upper_band[i] / close[i] - 1) * 100 > st_lower_band and
                (ds_upper_band[i] / close[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_short_upper_limit and
                rsi[i] > rsi_short_lower_limit and
                np.isnan(deal_type) and
                (bb_rsi_lower[i] > bb_short_limit
                    if bb_filter else True) and
                (adx[i] < adx_short_upper_limit and
                    adx[i] > adx_short_lower_limit
                    if adx_filter else True) and
                (equity > min_capital) and
                (direction == 0 or direction == 2)
            )

            if entry_short:
                deal_type = 1
                entry_signal = 1
                entry_price = close[i]

                if order_size_type == 0:
                    initial_position = (
                        equity * leverage * (order_size / 100.0)
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                elif order_size_type == 1:
                    initial_position = (
                        order_size * leverage
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )

                entry_date = time[i]
                liquidation_price = adjust(
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    ds_upper_band[i] * (100 + stop) / 100, p_precision
                )
                take_price[0][i] = adjust(
                    close[i] * (100 - take_percent[0]) / 100, p_precision
                )
                take_price[1][i] = adjust(
                    close[i] * (100 - take_percent[1]) / 100, p_precision
                )
                take_price[2][i] = adjust(
                    close[i] * (100 - take_percent[2]) / 100, p_precision
                )
                take_price[3][i] = adjust(
                    close[i] * (100 - take_percent[3]) / 100, p_precision
                )
                take_price[4][i] = adjust(
                    close[i] * (100 - take_percent[4]) / 100, p_precision
                )
                position_size = adjust(
                    position_size, q_precision
                )
                qty_take[0] = adjust(
                    position_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = adjust(
                    position_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = adjust(
                    position_size * take_volume[2] / 100, q_precision
                )
                qty_take[3] = adjust(
                    position_size * take_volume[3] / 100, q_precision
                )
                qty_take[4] = adjust(
                    position_size * take_volume[4] / 100, q_precision
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
            alert_long_new_stop,
            alert_short_new_stop
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

        if self.alert_long_new_stop:
            self.client.cancel_stop(symbol=self.symbol, side='Sell')
            self.order_ids['stop_ids'] = self.client.check_stop_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['stop_ids']
            )
            order_id = self.client.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)
        
        if self.alert_short_new_stop:
            self.client.cancel_stop(symbol=self.symbol, side='Buy')
            self.order_ids['stop_ids'] = self.client.check_stop_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['stop_ids']
            )
            order_id = self.client.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

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
                size=f'{self.params['take_volume'][0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[4][-1],
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
                size=f'{self.params['take_volume'][0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        self.cache.save(self.symbol, self.order_ids)