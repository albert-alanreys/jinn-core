import random as rand

import numpy as np
import numba as nb

from ... import math
from ... import ta


class NuggetV5():
    # Strategy parameters
    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    margin_type = 0
    # direction: 0 - 'all', 1 — 'longs', 2 — 'shorts'
    direction = 0
    initial_capital = 10000.0
    min_capital = 100.0
    commission = 0.075
    # order_size_type: 0 — 'PERCENT', 1 — 'CURRENCY'
    order_size_type = 0
    order_size = 100
    leverage = 1
    stop = 2.8
    atr_length = 14
    take_value = [3.0, 4.0, 5.0, 6.0, 7.0]
    take_volume = [10.0, 10.0, 50.0, 20.0, 10.0]
    st_atr_period = 6
    st_factor = 24.6
    st_upper_limit = 5.8
    st_lower_limit = 2.9
    k_length = 14
    d_length = 3
    k_d_long_limit = 20.0
    k_d_short_limit = 80.0
    adx_filter = False
    di_length = 14
    adx_length = 6
    adx_long_upper_limit = 44.0
    adx_long_lower_limit = 28.0
    adx_short_upper_limit = 77.0
    adx_short_lower_limit = 1.0

    # Parameters to be optimized and their possible values
    opt_parameters = {
        'stop': [i / 10 for i in range(1, 31)],
        'atr_length': [i for i in range(1, 21)],
        'take_value': [   
            sorted([
                float(rand.randint(2, 6)),
                float(rand.randint(7, 10)),
                float(rand.randint(11, 16)),
                float(rand.randint(17, 21)),
                float(rand.randint(22, 30))
            ])
            for i in range(1000)
        ],
        'take_volume': [
            math.random_trading_volumes(5, 10, 10)
            for i in range(1000)
        ],
        'st_atr_period': [i for i in range(2, 21)],
        'st_factor': [i / 100 for i in range(1000, 2501, 5)],
        'st_upper_limit': [i / 10 for i in range(39, 71)],
        'st_lower_limit': [i / 10 for i in range(11, 37)],
        'k_length': [i for i in range(3, 14)],
        'd_length': [i for i in range(3, 25)],
        'k_d_long_limit': [float(i) for i in range(5, 40)],
        'k_d_short_limit': [float(i) for i in range(60, 95)],
        'adx_filter': [False, True],
        'di_length': [i for i in range(1, 21)],
        'adx_length': [i for i in range(1, 21)],
        'adx_long_upper_limit': [float(i) for i in range(29, 51)],
        'adx_long_lower_limit': [float(i) for i in range(1, 29)],
        'adx_short_upper_limit': [float(i) for i in range(69, 101)],
        'adx_short_lower_limit': [float(i) for i in range(1, 69)]
    }

    # For frontend
    indicator_options = {
        'Stop-loss': {'color': '#FF0000'},
        'Take-profit #1': {'color': '#008000'},
        'Take-profit #2': {'color': '#008000'},
        'Take-profit #3': {'color': '#008000'},
        'Take-profit #4': {'color': '#008000'},
        'Take-profit #5': {'color': '#008000'}
    }

    # Class attributes
    class_attributes = (
        'opt_parameters',
        'indicator_options',
        'class_attributes',
        'start',
        'calculate',
        'trade'
    )

    def __init__(self, client, opt_parameters=None, all_parameters=None):
        self.client = client

        for key, value in NuggetV5.__dict__.items():
            if (not key.startswith('__') and
                    key not in NuggetV5.class_attributes):
                self.__dict__[key] = value

        if opt_parameters is not None:
            self.stop = opt_parameters[0]
            self.atr_length = opt_parameters[1]
            self.take_value = opt_parameters[2]
            self.take_volume = opt_parameters[3]
            self.st_atr_period = opt_parameters[4]
            self.st_factor = opt_parameters[5]
            self.st_upper_limit = opt_parameters[6]
            self.st_lower_limit = opt_parameters[7]
            self.k_length = opt_parameters[8]
            self.d_length = opt_parameters[9]
            self.k_d_long_limit = opt_parameters[10]
            self.k_d_short_limit = opt_parameters[11]
            self.adx_filter = opt_parameters[12]
            self.di_length = opt_parameters[13]
            self.adx_length = opt_parameters[14]
            self.adx_long_upper_limit = opt_parameters[15]
            self.adx_long_lower_limit = opt_parameters[16]
            self.adx_short_upper_limit = opt_parameters[17]
            self.adx_short_lower_limit = opt_parameters[18]

        if all_parameters is not None:
            self.margin_type = all_parameters[0]
            self.direction = all_parameters[1]
            self.initial_capital = all_parameters[2]
            self.min_capital = all_parameters[3]
            self.commission = all_parameters[4]
            self.order_size_type = all_parameters[5]
            self.order_size = all_parameters[6]
            self.leverage = all_parameters[7]
            self.stop = all_parameters[8]
            self.atr_length = all_parameters[9]
            self.take_value = all_parameters[10]
            self.take_volume = all_parameters[11]
            self.st_atr_period = all_parameters[12]
            self.st_factor = all_parameters[13]
            self.st_upper_limit = all_parameters[14]
            self.st_lower_limit = all_parameters[15]
            self.k_length = all_parameters[16]
            self.d_length = all_parameters[17]
            self.k_d_long_limit = all_parameters[18]
            self.k_d_short_limit = all_parameters[19]
            self.adx_filter = all_parameters[20]
            self.di_length = all_parameters[21]
            self.adx_length = all_parameters[22]
            self.adx_long_upper_limit = all_parameters[23]
            self.adx_long_lower_limit = all_parameters[24]
            self.adx_short_upper_limit = all_parameters[25]
            self.adx_short_lower_limit = all_parameters[26]

    def start(self):
        self.price_precision = self.client.price_precision
        self.qty_precision = self.client.qty_precision
        self.time = self.client.price_data[:, 0]
        self.high = self.client.price_data[:, 2]
        self.low = self.client.price_data[:, 3]
        self.close = self.client.price_data[:, 4]
        self.equity = self.initial_capital
        self.completed_deals_log = np.array([])
        self.open_deals_log = np.full(5, np.nan)
        self.deal_type = np.nan
        self.entry_signal = np.nan
        self.entry_date = np.nan
        self.entry_price = np.nan
        self.liquidation_price = np.nan
        self.take_price = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.position_size = np.nan
        self.qty_take = np.full(5, np.nan)
        self.atr = ta.atr(self.high, self.low, self.close, self.atr_length)
        self.ds = ta.ds(self.high, self.low, self.close,
                        self.st_factor, self.st_atr_period)
        self.st_upper_band_changed = ta.change(self.ds[0], 1)
        self.st_lower_band_changed = ta.change(self.ds[1], 1)
        self.k = ta.stoch(self.close, self.high, self.low, self.k_length)
        self.d = ta.sma(self.k, self.d_length)

        if self.adx_filter:
            self.adx = ta.dmi(
                self.high, self.low, self.close,
                self.di_length, self.adx_length)[2]
        else:
            self.adx = np.full(self.time.shape[0], np.nan)

        self.alert_long = False
        self.alert_short = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False
        self.alert_cancel = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.take_price,
            self.stop_price,
            self.alert_long,
            self.alert_short,
            self.alert_long_new_stop,
            self.alert_short_new_stop,
            self.alert_cancel
        ) = self.calculate(
                self.direction,
                self.initial_capital,
                self.min_capital,
                self.commission,
                self.order_size_type,
                self.order_size,
                self.leverage,
                self.stop,
                self.take_value,
                self.take_volume,
                self.st_upper_limit,
                self.st_lower_limit,
                self.k_d_long_limit,
                self.k_d_short_limit,
                self.adx_filter,
                self.adx_long_upper_limit,
                self.adx_long_lower_limit,
                self.adx_short_upper_limit,
                self.adx_short_lower_limit,
                self.price_precision,
                self.qty_precision,
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
                self.atr,
                self.ds[0],
                self.ds[1],
                self.st_upper_band_changed,
                self.st_lower_band_changed,
                self.k,
                self.d,
                self.adx,
                self.alert_long,
                self.alert_short,
                self.alert_long_new_stop,
                self.alert_short_new_stop,
                self.alert_cancel
        )

        self.indicators = {
            'Stop-loss': {
                'options': self.indicator_options['Stop-loss'],
                'values': self.stop_price
            },
            'Take-profit #1': {
                'options': self.indicator_options['Take-profit #1'],
                'values': self.take_price[0]
            },
            'Take-profit #2': {
                'options': self.indicator_options['Take-profit #2'],
                'values': self.take_price[1]
            },
            'Take-profit #3': {
                'options': self.indicator_options['Take-profit #3'],
                'values': self.take_price[2]
            },
            'Take-profit #4': {
                'options': self.indicator_options['Take-profit #4'],
                'values': self.take_price[3]
            },
            'Take-profit #5': {
                'options': self.indicator_options['Take-profit #5'],
                'values': self.take_price[4]
            }
        }

    @staticmethod
    @nb.jit(
        (
            nb.int8,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.types.List(nb.float64, reflected=True),
            nb.types.List(nb.float64, reflected=True),
            nb.float32,
            nb.float32,
            nb.float32,
            nb.float32,
            nb.boolean,
            nb.float32,
            nb.float32,
            nb.float32,
            nb.float32,
            nb.float64,
            nb.float64,
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64,
            nb.float64[:],
            nb.float64[:],
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64[:, :],
            nb.float64[:],
            nb.float64,
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean
        ),
        cache=True,
        nopython=True,
        nogil=True
    )
    def calculate(
        direction,
        initial_capital,
        min_capital,
        commission,
        order_size_type,
        order_size,
        leverage,
        stop,
        take_value,
        take_volume,
        st_upper_limit,
        st_lower_limit,
        k_d_long_limit,
        k_d_short_limit,
        adx_filter,
        adx_long_upper_limit,
        adx_long_lower_limit,
        adx_short_upper_limit,
        adx_short_lower_limit,
        price_precision,
        qty_precision,
        time,
        high,
        low,
        close,
        equity,
        completed_deals_log,
        open_deals_log,
        deal_type,
        entry_signal,
        entry_date,
        entry_price,
        liquidation_price,
        take_price,
        stop_price,
        position_size,
        qty_take,
        atr,
        ds_upper_band,
        ds_lower_band,
        st_upper_band_changed,
        st_lower_band_changed,
        k,
        d,
        adx,
        alert_long,
        alert_short,
        alert_long_new_stop,
        alert_short_new_stop,
        alert_cancel
    ):
        def round_to_minqty_or_mintick(number, precision):
            return round(round(number / precision) * precision, 8)

        def update_log(log, equity, commission, deal_type, entry_signal,
                       exit_signal, entry_date, exit_date, entry_price,
                       exit_price, position_size, initial_capital):
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
            alert_long = False
            alert_short = False
            alert_long_new_stop = False
            alert_short_new_stop = False
            alert_cancel = False

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
                    alert_cancel = True

                if (st_lower_band_changed[i] and
                        ((ds_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = round_to_minqty_or_mintick(
                        ds_lower_band[i] * (100 - stop) / 100,
                        price_precision
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
                    alert_cancel = True

            entry_long = (
                (close[i] / ds_lower_band[i] - 1) * 100 > st_lower_limit and
                (close[i] / ds_lower_band[i] - 1) * 100 < st_upper_limit and
                k[i] < k_d_long_limit and
                d[i] < k_d_long_limit and
                np.isnan(deal_type) and
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
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 - (1 / leverage)), price_precision
                )
                stop_price[i] = round_to_minqty_or_mintick(
                    ds_lower_band[i] * (100 - stop) / 100, price_precision
                )
                take_price[0][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[0] * atr[i], price_precision
                )
                take_price[1][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[1] * atr[i], price_precision
                )
                take_price[2][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[2] * atr[i], price_precision
                )
                take_price[3][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[3] * atr[i], price_precision
                )
                take_price[4][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[4] * atr[i], price_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, qty_precision
                )
                qty_take[0] = round_to_minqty_or_mintick(
                    position_size * take_volume[0] / 100, qty_precision
                )
                qty_take[1] = round_to_minqty_or_mintick(
                    position_size * take_volume[1] / 100, qty_precision
                )
                qty_take[2] = round_to_minqty_or_mintick(
                    position_size * take_volume[2] / 100, qty_precision
                )
                qty_take[3] = round_to_minqty_or_mintick(
                    position_size * take_volume[3] / 100, qty_precision
                )
                qty_take[4] = round_to_minqty_or_mintick(
                    position_size * take_volume[4] / 100, qty_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_long = True

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
                    alert_cancel = True 

                if (st_upper_band_changed[i] and
                        ((ds_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = round_to_minqty_or_mintick(
                        (ds_upper_band[i] * (100 + stop) / 100), 
                        price_precision
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
                    alert_cancel = True

            entry_short = (
                (ds_upper_band[i] / close[i] - 1) * 100 > st_lower_limit and
                (ds_upper_band[i] / close[i] - 1) * 100 < st_upper_limit and
                k[i] > k_d_short_limit and
                d[i] > k_d_short_limit and
                np.isnan(deal_type) and
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
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 + (1 / leverage)), price_precision
                )
                stop_price[i] = round_to_minqty_or_mintick(
                    ds_upper_band[i] * (100 + stop) / 100, price_precision
                )
                take_price[0][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[0] * atr[i], price_precision
                )
                take_price[1][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[1] * atr[i], price_precision
                )
                take_price[2][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[2] * atr[i], price_precision
                )
                take_price[3][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[3] * atr[i], price_precision
                )
                take_price[4][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[4] * atr[i], price_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, qty_precision
                )
                qty_take[0] = round_to_minqty_or_mintick(
                    position_size * take_volume[0] / 100, qty_precision
                )
                qty_take[1] = round_to_minqty_or_mintick(
                    position_size * take_volume[1] / 100, qty_precision
                )
                qty_take[2] = round_to_minqty_or_mintick(
                    position_size * take_volume[2] / 100, qty_precision
                )
                qty_take[3] = round_to_minqty_or_mintick(
                    position_size * take_volume[3] / 100, qty_precision
                )
                qty_take[4] = round_to_minqty_or_mintick(
                    position_size * take_volume[4] / 100, qty_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_short = True

        return (
            completed_deals_log,
            open_deals_log,
            take_price,
            stop_price,
            alert_long,
            alert_short,
            alert_long_new_stop,
            alert_short_new_stop,
            alert_cancel
        )
    
    def trade(self):
        if self.alert_cancel:
            self.client.futures_cancel_all_orders(
                symbol=self.client.symbol
            )

        self.client.check_stop_status(self.client.symbol)
        self.client.check_limit_status(self.client.symbol)

        if self.alert_long_new_stop:
            self.client.futures_cancel_stop(
                symbol=self.client.symbol, 
                side='Sell'
            )
            self.client.check_stop_status(self.client.symbol)
            self.client.futures_market_stop_sell(
                symbol=self.client.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
        
        if self.alert_short_new_stop:
            self.client.futures_cancel_stop(
                symbol=self.client.symbol, 
                side='Buy'
            )
            self.client.check_stop_status(self.client.symbol)
            self.client.futures_market_stop_buy(
                symbol=self.client.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )

        if self.alert_long:
            self.client.futures_market_open_buy(
                symbol=self.client.symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=str(self.leverage),
                hedge='false'
            )
            self.client.futures_market_stop_sell(
                symbol=self.client.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=self.client.symbol,
                size=f'{self.take_volume[0]}%',
                price=self.take_price[0][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=self.client.symbol,
                size=f'{self.take_volume[1]}%',
                price=self.take_price[1][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=self.client.symbol,
                size=f'{self.take_volume[2]}%',
                price=self.take_price[2][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=self.client.symbol,
                size=f'{self.take_volume[3]}%',
                price=self.take_price[3][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=self.client.symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge='false'
            )
        
        if self.alert_short:
            self.client.futures_market_open_sell(
                symbol=self.client.symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=str(self.leverage),
                hedge='false'
            )
            self.client.futures_market_stop_buy(
                symbol=self.client.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=self.client.symbol,
                size=f'{self.take_volume[0]}%',
                price=self.take_price[0][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=self.client.symbol,
                size=f'{self.take_volume[1]}%',
                price=self.take_price[1][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=self.client.symbol,
                size=f'{self.take_volume[2]}%',
                price=self.take_price[2][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=self.client.symbol,
                size=f'{self.take_volume[3]}%',
                price=self.take_price[3][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=self.client.symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge='false'
            )