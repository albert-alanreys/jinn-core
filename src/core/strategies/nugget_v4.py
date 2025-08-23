from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import numba as nb

import src.core.quantklines as qk
from src.shared.constants import colors
from src.shared.utils import adjust

from . import BaseStrategy
from . import update_completed_deals_log

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient


class NuggetV4(BaseStrategy):
    # Strategy parameters
    params = {
        'min_capital': 100.0,
        'stop_type': 1,
        'stop': 1.0,
        'trail_stop': 4,
        'trail_percent': 0.0,
        'take_volume_1': [10.0, 10.0, 10.0, 10.0, 60.0],
        'take_volume_2': [
            10.0, 5.0, 5.0, 5.0, 5.0,
            5.0, 10.0, 15.0, 10.0, 30.0
        ],
        'st_atr_period': 7,
        'st_factor': 10.5,
        'st_upper_band': 4.8,
        'st_lower_band': 2.2,
        'rsi_length': 7,
        'rsi_long_upper_limit': 47.0,
        'rsi_long_lower_limit': 1.0,
        'rsi_short_upper_limit': 100.0,
        'rsi_short_lower_limit': 58.0,
        'bb_filter': False,
        'ma_length': 6,
        'bb_mult': 2.5,
        'bb_long_limit': 44.0,
        'bb_short_limit': 55.0,
        'pivot_bars': 2,
        'look_back': 35,
        'channel_range': 7.0
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_type': [i for i in range(3, 4)],
        'stop': [i / 10 for i in range(1, 11)],
        'trail_stop': [i for i in range(0, 9)],
        'trail_percent': [float(i) for i in range(0, 51, 1)],
        'take_volume_1': [
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
        'take_volume_2': [
            [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            [25.0, 20.0, 15.0, 10.0, 8.0, 6.0, 5.0, 4.0, 3.0, 4.0],
            [4.0, 3.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 25.0, 4.0],
            [5.0, 10.0, 15.0, 20.0, 15.0, 10.0, 8.0, 7.0, 5.0, 5.0],
            [12.0, 12.0, 12.0, 12.0, 12.0, 10.0, 8.0, 7.0, 7.0, 8.0],
            [8.0, 8.0, 15.0, 15.0, 12.0, 12.0, 10.0, 10.0, 5.0, 5.0],
            [30.0, 20.0, 12.0, 8.0, 6.0, 5.0, 5.0, 5.0, 4.0, 5.0],
            [5.0, 5.0, 5.0, 6.0, 8.0, 12.0, 20.0, 30.0, 5.0, 4.0],
            [18.0, 15.0, 12.0, 10.0, 10.0, 8.0, 7.0, 6.0, 6.0, 8.0],
            [8.0, 6.0, 6.0, 7.0, 8.0, 10.0, 10.0, 12.0, 15.0, 18.0],
            [15.0, 10.0, 15.0, 10.0, 15.0, 10.0, 5.0, 5.0, 10.0, 5.0],
            [40.0, 15.0, 10.0, 8.0, 5.0, 5.0, 5.0, 5.0, 4.0, 3.0],
            [3.0, 4.0, 5.0, 5.0, 5.0, 8.0, 10.0, 15.0, 40.0, 5.0],
            [10.0, 12.0, 13.0, 12.0, 10.0, 8.0, 7.0, 8.0, 10.0, 10.0],
            [7.0, 9.0, 11.0, 13.0, 15.0, 13.0, 11.0, 9.0, 7.0, 5.0],
            [20.0, 5.0, 20.0, 5.0, 20.0, 5.0, 10.0, 5.0, 5.0, 5.0],
            [12.0, 12.0, 8.0, 8.0, 12.0, 12.0, 8.0, 8.0, 10.0, 10.0],
            [6.0, 12.0, 18.0, 6.0, 12.0, 18.0, 6.0, 12.0, 6.0, 4.0],
            [9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 9.0, 11.0, 10.0, 10.0],
            [25.0, 10.0, 10.0, 10.0, 5.0, 5.0, 5.0, 5.0, 10.0, 15.0]
        ],
        'st_atr_period': [i for i in range(2, 21)],
        'st_factor': [i / 100 for i in range(1000, 2501, 5)],
        'st_upper_band': [i / 10 for i in range(46, 71)],
        'st_lower_band': [i / 10 for i in range(10, 41)],
        'rsi_length': [i for i in range(3, 22)],
        'rsi_long_upper_limit': [float(i) for i in range(29, 51)],
        'rsi_long_lower_limit': [float(i) for i in range(1, 29)],
        'rsi_short_upper_limit': [float(i) for i in range(68, 101)],
        'rsi_short_lower_limit': [float(i) for i in range(50, 68)],
        'bb_filter': [True, False],
        'ma_length': [i for i in range(3, 26)],
        'bb_mult': [i / 10 for i in range(10, 31)],
        'bb_long_limit': [float(i) for i in range(20, 51)],
        'bb_short_limit': [float(i) for i in range(50, 81)],
        'pivot_bars': [i for i in range(1, 21)],
        'look_back': [i for i in range(10, 101, 5)],
        'channel_range': [float(i) for i in range(3, 21)]
    }

    # Frontend rendering settings for indicators
    indicator_options = {
        'SL': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON
        },
        'TP #1': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #2': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #3': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #4': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #5': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #6': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #7': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #8': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #9': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        },
        'TP #10': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        }
    }

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)

    def calculate(self, market_data) -> None:
        super().init_variables(market_data)

        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.liquidation_price = np.nan

        self.qty_take_1 = np.full(5, np.nan)
        self.qty_take_2 = np.full(10, np.nan)

        self.stop_moved = False

        self.grid_type = np.nan
        self.pivot_LH_bar_index = np.array([])
        self.pivot_HL_bar_index = np.array([])
        self.last_channel_range = np.nan
        self.last_pivot_LH = np.array([])
        self.last_pivot_HL = np.array([])
        self.last_pivot = np.nan
        self.pivot_HH = np.nan
        self.pivot_LL = np.nan

        self.dst = qk.dst(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['st_factor'],
            atr_length=self.params['st_atr_period']
        )
        self.change_upper_band = qk.change(source=self.dst[0], length=1)
        self.change_lower_band = qk.change(source=self.dst[1], length=1)
        self.rsi = qk.rsi(source=self.close, length=self.params['rsi_length'])

        if self.params['bb_filter']:
            self.bb_rsi = qk.bb(
                source=self.rsi,
                length=self.params['ma_length'],
                mult=self.params['bb_mult']
            )
        else:
            self.bb_rsi = np.full(self.time.shape[0], np.nan)

        self.pivot_LH = qk.pivothigh(
            source=self.high,
            leftbars=self.params['pivot_bars'],
            rightbars=self.params['pivot_bars']
        )
        self.pivot_HL = qk.pivotlow(
            source=self.low,
            leftbars=self.params['pivot_bars'],
            rightbars=self.params['pivot_bars']
        )

        self.fibo_values = np.array(
            [
                0.0, 0.236, 0.382, 0.5, 0.618, 0.8, 1.0,
                1.618, 2.0, 2.618, 3.0, 3.618, 4.0
            ]
        )
        self.fibo_levels = np.full(13, np.nan)
        self.alert_cancel = False
        self.alert_open_long_1 = False
        self.alert_open_long_2 = False
        self.alert_open_short_1 = False
        self.alert_open_short_2 = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.stop_price,
            self.take_price,
            self.alert_cancel,
            self.alert_open_long_1,
            self.alert_open_long_2,
            self.alert_open_short_1,
            self.alert_open_short_2,
            self.alert_long_new_stop,
            self.alert_short_new_stop
        ) = self._calculate_loop(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['min_capital'],
            self.params['commission'],
            self.params['position_size_type'],
            self.params['position_size'],
            self.params['leverage'],
            self.params['stop_type'],
            self.params['stop'],
            self.params['trail_stop'],
            self.params['trail_percent'],
            self.params['take_volume_1'],
            self.params['take_volume_2'],
            self.params['st_upper_band'],
            self.params['st_lower_band'],
            self.params['rsi_long_upper_limit'],
            self.params['rsi_long_lower_limit'],
            self.params['rsi_short_upper_limit'],
            self.params['rsi_short_lower_limit'],
            self.params['bb_filter'],
            self.params['bb_long_limit'],
            self.params['bb_short_limit'],
            self.params['pivot_bars'],
            self.params['look_back'],
            self.params['channel_range'],
            self.p_precision,
            self.q_precision,
            self.time,
            self.high,
            self.low,
            self.close,
            self.equity,
            self.completed_deals_log,
            self.open_deals_log,
            self.position_type,
            self.order_signal,
            self.order_date,
            self.order_price,
            self.liquidation_price,
            self.order_size,
            self.stop_price,
            self.take_price,
            self.qty_take_1,
            self.qty_take_2,
            self.stop_moved,
            self.grid_type,
            self.pivot_LH_bar_index,
            self.pivot_HL_bar_index,
            self.last_channel_range,
            self.last_pivot_LH,
            self.last_pivot_HL,
            self.last_pivot,
            self.pivot_HH,
            self.pivot_LL,
            self.dst[0],
            self.dst[1],
            self.change_upper_band,
            self.change_lower_band,
            self.rsi,
            self.bb_rsi[1] if self.params['bb_filter'] else self.bb_rsi,
            self.bb_rsi[2] if self.params['bb_filter'] else self.bb_rsi,
            self.pivot_LH,
            self.pivot_HL,
            self.fibo_values,
            self.fibo_levels,
            self.alert_cancel,
            self.alert_open_long_1,
            self.alert_open_long_2,
            self.alert_open_short_1,
            self.alert_open_short_2,
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
            },
            'TP #6': {
                'options': self.indicator_options['TP #6'],
                'values': self.take_price[5]
            },
            'TP #7': {
                'options': self.indicator_options['TP #7'],
                'values': self.take_price[6]
            },
            'TP #8': {
                'options': self.indicator_options['TP #8'],
                'values': self.take_price[7]
            },
            'TP #9': {
                'options': self.indicator_options['TP #9'],
                'values': self.take_price[8]
            },
            'TP #10': {
                'options': self.indicator_options['TP #10'],
                'values': self.take_price[9]
            }
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        direction: int,
        initial_capital: float,
        min_capital: float,
        commission: float,
        position_size_type: int,
        position_size: float,
        leverage: int,
        stop_type: int,
        stop: float,
        trail_stop: int,
        trail_percent: float,
        take_volume_1: list,
        take_volume_2: list,
        st_upper_band: float,
        st_lower_band: float,
        rsi_long_upper_limit: float,
        rsi_long_lower_limit: float,
        rsi_short_upper_limit: float,
        rsi_short_lower_limit: float,
        bb_filter: bool,
        bb_long_limit: float,
        bb_short_limit: float,
        pivot_bars: int,
        look_back: int,
        channel_range: float,
        p_precision: float,
        q_precision: float,
        time: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        equity: float,
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray,
        position_type: float,
        order_signal: float,
        order_date: float,
        order_price: float,
        liquidation_price: float,
        order_size: float,
        stop_price: np.ndarray,
        take_price: np.ndarray,
        qty_take_1: np.ndarray,
        qty_take_2: np.ndarray,
        stop_moved: int,
        grid_type: float,
        pivot_LH_bar_index: np.ndarray,
        pivot_HL_bar_index: np.ndarray,
        last_channel_range: float,
        last_pivot_LH: np.ndarray,
        last_pivot_HL: np.ndarray,
        last_pivot: float,
        pivot_HH: float,
        pivot_LL: float,
        dst_upper_band: np.ndarray,
        dst_lower_band: np.ndarray,
        change_upper_band: np.ndarray,
        change_lower_band: np.ndarray,
        rsi: np.ndarray,
        bb_rsi_upper: np.ndarray,
        bb_rsi_lower: np.ndarray,
        pivot_LH: np.ndarray,
        pivot_HL: np.ndarray,
        fibo_values: np.ndarray,
        fibo_levels: np.ndarray,
        alert_cancel: bool,
        alert_open_long_1: bool,
        alert_open_long_2: bool,
        alert_open_short_1: bool,
        alert_open_short_2: bool,
        alert_long_new_stop: bool,
        alert_short_new_stop: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_price[:, i] = take_price[:, i - 1]

            alert_cancel = False
            alert_open_long_1 = False
            alert_open_long_2 = False
            alert_open_short_1 = False
            alert_open_short_2 = False
            alert_long_new_stop = False
            alert_short_new_stop = False

            # Indicators
            if pivot_LH_bar_index.shape[0] > 0:
                if i - pivot_LH_bar_index[0] > look_back:
                    pivot_LH_bar_index = pivot_LH_bar_index[1:]
                    last_pivot_LH = last_pivot_LH[1:]

                    if last_pivot_LH.shape[0] > 0:
                        pivot_HH = last_pivot_LH.max()
                    else:
                        pivot_HH = np.nan

            if pivot_HL_bar_index.shape[0] > 0:
                if i - pivot_HL_bar_index[0] > look_back:
                    pivot_HL_bar_index = pivot_HL_bar_index[1:]
                    last_pivot_HL = last_pivot_HL[1:]

                    if last_pivot_HL.shape[0] > 0:
                        pivot_LL = last_pivot_HL.min()
                    else:
                        pivot_LL = np.nan

            if not np.isnan(pivot_LH[i]):
                if last_pivot_LH.shape[0] > 0:
                    if (pivot_LH[i] >= last_pivot_LH.max() or
                            np.isnan(pivot_HH)):
                        pivot_HH = pivot_LH[i]
                        last_pivot = 0
                elif np.isnan(pivot_HH):
                    pivot_HH = pivot_LH[i]
                    last_pivot = 0

                pivot_LH_bar_index = np.concatenate(
                    (pivot_LH_bar_index, np.array([i - pivot_bars]))
                )
                last_pivot_LH = np.concatenate(
                    (last_pivot_LH, np.array([high[i - pivot_bars]]))
                )

            if not np.isnan(pivot_HL[i]):
                if last_pivot_HL.shape[0] > 0:
                    if (pivot_HL[i] <= last_pivot_HL.min() or 
                            np.isnan(pivot_LL)):
                        pivot_LL = pivot_HL[i]
                        last_pivot = 1
                elif np.isnan(pivot_LL):
                    pivot_LL = pivot_HL[i]
                    last_pivot = 1

                pivot_HL_bar_index = np.concatenate(
                    (pivot_HL_bar_index, np.array([i - pivot_bars]))
                )
                last_pivot_HL = np.concatenate(
                    (last_pivot_HL, np.array([low[i - pivot_bars]]))
                )

            # Check of liquidation
            if (position_type == 0 and low[i] <= liquidation_price):
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    700,
                    order_date,
                    time[i],
                    order_price,
                    liquidation_price,
                    order_size,
                    initial_capital
                )
                equity += pnl
                
                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                stop_price[i] = np.nan
                take_price[:, i] = np.nan
                qty_take_1[:] = np.nan
                qty_take_2[:] = np.nan
                stop_moved = False
                grid_type = np.nan
                alert_cancel = True

            if (position_type == 1 and high[i] >= liquidation_price):
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    800,
                    order_date,
                    time[i],
                    order_price,
                    liquidation_price,
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                stop_price[i] = np.nan
                take_price[:, i] = np.nan
                qty_take_1[:] = np.nan
                qty_take_2[:] = np.nan
                stop_moved = False
                grid_type = np.nan
                alert_cancel = True

            # Trading logic (longs)
            if position_type == 0:
                if low[i] <= stop_price[i]:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        500,
                        order_date,
                        time[i],
                        order_price,
                        stop_price[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    stop_price[i] = np.nan
                    take_price[:, i] = np.nan
                    qty_take_1[:] = np.nan
                    qty_take_2[:] = np.nan
                    stop_moved = False
                    grid_type = np.nan
                    alert_cancel = True

                if (stop_type == 1 and
                        change_lower_band[i] and
                        ((dst_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = adjust(
                        dst_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                    alert_long_new_stop = True
                elif (stop_type == 2 or stop_type == 3) and not stop_moved:
                    take = None

                    if grid_type == 0:
                        if (trail_stop == 4 and
                                high[i] >= take_price[3, i]):
                            take = take_price[3, i]
                        elif (trail_stop == 3 and
                                high[i] >= take_price[2, i]):
                            take = take_price[2, i]
                        elif (trail_stop == 2 and
                                high[i] >= take_price[1, i]):
                            take = take_price[1, i]
                        elif (trail_stop == 1 and
                                high[i] >= take_price[0, i]):
                            take = take_price[0, i]
                    elif grid_type == 1:
                        if (trail_stop == 9 and
                                high[i] >= take_price[8, i]):
                            take = take_price[8, i]
                        elif (trail_stop == 8 and
                                high[i] >= take_price[7, i]):
                            take = take_price[7, i]
                        elif (trail_stop == 7 and
                                high[i] >= take_price[6, i]):
                            take = take_price[6, i]
                        elif (trail_stop == 6 and
                                high[i] >= take_price[5, i]):
                            take = take_price[5, i]
                        elif (trail_stop == 5 and
                                high[i] >= take_price[4, i]):
                            take = take_price[4, i]
                        elif (trail_stop == 4 and
                                high[i] >= take_price[3, i]):
                            take = take_price[3, i]
                        elif (trail_stop == 3 and
                                high[i] >= take_price[2, i]):
                            take = take_price[2, i]
                        elif (trail_stop == 2 and
                                high[i] >= take_price[1, i]):
                            take = take_price[1, i]
                        elif (trail_stop == 1 and
                                high[i] >= take_price[0, i]):
                            take = take_price[0, i]

                    if take is not None:
                        stop_moved = True
                        stop_price[i] = adjust(
                            (take - order_price) * (trail_percent / 100)
                                + order_price,
                            p_precision
                        )
                        alert_long_new_stop = True

                if grid_type == 0:
                    if (not np.isnan(take_price[0, i]) and 
                            high[i] >= take_price[0, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            301,
                            order_date,
                            time[i],
                            order_price,
                            take_price[0, i],
                            qty_take_1[0],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[0], 8)
                        open_deals_log[0][4] = order_size
                        take_price[0, i] = np.nan
                        qty_take_1[0] = np.nan

                    if (not np.isnan(take_price[1, i]) and 
                            high[i] >= take_price[1, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            302,
                            order_date,
                            time[i],
                            order_price,
                            take_price[1, i],
                            qty_take_1[1],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[1], 8)
                        open_deals_log[0][4] = order_size
                        take_price[1, i] = np.nan
                        qty_take_1[1] = np.nan

                    if (not np.isnan(take_price[2, i]) and 
                            high[i] >= take_price[2, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            303,
                            order_date,
                            time[i],
                            order_price,
                            take_price[2, i],
                            qty_take_1[2],
                            initial_capital
                        ) 
                        equity += pnl

                        order_size = round(order_size - qty_take_1[2], 8)
                        open_deals_log[0][4] = order_size
                        take_price[2, i] = np.nan
                        qty_take_1[2] = np.nan

                    if (not np.isnan(take_price[3, i]) and 
                            high[i] >= take_price[3, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            304,
                            order_date,
                            time[i],
                            order_price,
                            take_price[3, i],
                            qty_take_1[3],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[3], 8)
                        open_deals_log[0][4] = order_size
                        take_price[3, i] = np.nan
                        qty_take_1[3] = np.nan

                    if (not np.isnan(take_price[4, i]) and 
                            high[i] >= take_price[4, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            305,
                            order_date,
                            time[i],
                            order_price,
                            take_price[4, i],
                            round(qty_take_1[4], 8),
                            initial_capital
                        )
                        equity += pnl

                        open_deals_log[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[4, i] = np.nan
                        qty_take_1[4] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True
                elif grid_type == 1:
                    if (not np.isnan(take_price[0, i]) and 
                            high[i] >= take_price[0, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            301,
                            order_date,
                            time[i],
                            order_price,
                            take_price[0, i],
                            qty_take_2[0],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[0], 8)
                        open_deals_log[0][4] = order_size
                        take_price[0, i] = np.nan
                        qty_take_2[0] = np.nan

                    if (not np.isnan(take_price[1, i]) and 
                            high[i] >= take_price[1, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            302,
                            order_date,
                            time[i],
                            order_price,
                            take_price[1, i],
                            qty_take_2[1],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[1], 8)
                        open_deals_log[0][4] = order_size
                        take_price[1, i] = np.nan
                        qty_take_2[1] = np.nan

                    if (not np.isnan(take_price[2, i]) and 
                            high[i] >= take_price[2, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            303,
                            order_date,
                            time[i],
                            order_price,
                            take_price[2, i],
                            qty_take_2[2],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[2], 8)
                        open_deals_log[0][4] = order_size
                        take_price[2, i] = np.nan
                        qty_take_2[2] = np.nan

                    if (not np.isnan(take_price[3, i]) and 
                            high[i] >= take_price[3, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            304,
                            order_date,
                            time[i],
                            order_price,
                            take_price[3, i],
                            qty_take_2[3],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[3], 8)
                        open_deals_log[0][4] = order_size
                        take_price[3, i] = np.nan
                        qty_take_2[3] = np.nan

                    if (not np.isnan(take_price[4, i]) and 
                            high[i] >= take_price[4, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            305,
                            order_date,
                            time[i],
                            order_price,
                            take_price[4, i],
                            qty_take_2[4],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[4], 8)
                        open_deals_log[0][4] = order_size
                        take_price[4, i] = np.nan
                        qty_take_2[4] = np.nan

                    if (not np.isnan(take_price[5, i]) and 
                            high[i] >= take_price[5, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            306,
                            order_date,
                            time[i],
                            order_price,
                            take_price[5, i],
                            qty_take_2[5],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[5], 8)
                        open_deals_log[0][4] = order_size
                        take_price[5, i] = np.nan
                        qty_take_2[5] = np.nan

                    if (not np.isnan(take_price[6, i]) and 
                            high[i] >= take_price[6, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            307,
                            order_date,
                            time[i],
                            order_price,
                            take_price[6, i],
                            qty_take_2[6],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[6], 8)
                        open_deals_log[0][4] = order_size
                        take_price[6, i] = np.nan
                        qty_take_2[6] = np.nan

                    if (not np.isnan(take_price[7, i]) and 
                            high[i] >= take_price[7, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            308,
                            order_date,
                            time[i],
                            order_price,
                            take_price[7, i],
                            qty_take_2[7],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[7], 8)
                        open_deals_log[0][4] = order_size
                        take_price[7, i] = np.nan
                        qty_take_2[7] = np.nan

                    if (not np.isnan(take_price[8, i]) and 
                            high[i] >= take_price[8, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            309,
                            order_date,
                            time[i],
                            order_price,
                            take_price[8, i],
                            qty_take_2[8],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[8], 8)
                        open_deals_log[0][4] = order_size
                        take_price[8, i] = np.nan
                        qty_take_2[8] = np.nan

                    if (not np.isnan(take_price[9, i]) and 
                            high[i] >= take_price[9, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            310,
                            order_date,
                            time[i],
                            order_price,
                            take_price[9, i],
                            round(qty_take_2[9], 8),
                            initial_capital
                        )
                        equity += pnl

                        open_deals_log[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[9, i] = np.nan
                        qty_take_2[9] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True

            pre_entry_long = (
                (close[i] / dst_lower_band[i] - 1) * 100 > st_lower_band and
                (close[i] / dst_lower_band[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_long_upper_limit and
                rsi[i] > rsi_long_lower_limit and
                np.isnan(position_type) and
                (bb_rsi_upper[i] < bb_long_limit
                    if bb_filter else True) and
                last_pivot == 1 and
                (equity > min_capital) and
                (direction == 0 or direction == 1)
            )

            if pre_entry_long:
                if not np.isnan(pivot_HH) and not np.isnan(pivot_LL):
                    last_channel_range = (pivot_HH / pivot_LL - 1) * 100

                    for j in range(fibo_values.shape[0]):
                        price = pivot_LL + (pivot_HH - pivot_LL) * fibo_values[j]
                        fibo_levels[j] = price

            entry_long = (
                pre_entry_long and 
                close[i] < fibo_levels[2] and
                close[i] >= fibo_levels[0]
            )

            if entry_long:
                position_type = 0
                order_signal = 100
                order_date = time[i]
                order_price = close[i]

                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                elif position_size_type == 1:
                    initial_position = (position_size * leverage)
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                    
                order_size = adjust(
                    order_size, q_precision
                )
                liquidation_price = adjust(
                    order_price * (1 - (1 / leverage)), p_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )

                if stop_type == 1 or stop_type == 2:
                    stop_price[i] = adjust(
                        dst_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                elif stop_type == 3:
                    stop_price[i] = adjust(
                        fibo_levels[0] * (100 - stop) / 100, p_precision
                    )

                if last_channel_range >= channel_range:
                    grid_type = 0

                    if close[i] >= fibo_levels[0] and close[i] < fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[2], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                    elif close[i] >= fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[7], p_precision
                        )

                    qty_take_1[0] = adjust(
                        order_size * take_volume_1[0] / 100, q_precision
                    )
                    qty_take_1[1] = adjust(
                        order_size * take_volume_1[1] / 100, q_precision
                    )
                    qty_take_1[2] = adjust(
                        order_size * take_volume_1[2] / 100, q_precision
                    )
                    qty_take_1[3] = adjust(
                        order_size * take_volume_1[3] / 100, q_precision
                    )
                    qty_take_1[4] = adjust(
                        order_size * take_volume_1[4] / 100, q_precision
                    )
                    alert_open_long_1 = True
                elif last_channel_range < channel_range:
                    grid_type = 1

                    if close[i] >= fibo_levels[0] and close[i] < fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[2], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[5, i] = adjust(
                            fibo_levels[7], p_precision
                        )
                        take_price[6, i] = adjust(
                            fibo_levels[8], p_precision
                        )
                        take_price[7, i] = adjust(
                            fibo_levels[9], p_precision
                        )
                        take_price[8, i] = adjust(
                            fibo_levels[10], p_precision
                        )
                        take_price[9, i] = adjust(
                            fibo_levels[11], p_precision
                        )
                    elif close[i] >= fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[7], p_precision
                        )
                        take_price[5, i] = adjust(
                            fibo_levels[8], p_precision
                        )
                        take_price[6, i] = adjust(
                            fibo_levels[9], p_precision
                        )
                        take_price[7, i] = adjust(
                            fibo_levels[10], p_precision
                        )
                        take_price[8, i] = adjust(
                            fibo_levels[11], p_precision
                        )
                        take_price[9, i] = adjust(
                            fibo_levels[12], p_precision
                        )

                    qty_take_2[0] = adjust(
                        order_size * take_volume_2[0] / 100, q_precision
                    )
                    qty_take_2[1] = adjust(
                        order_size * take_volume_2[1] / 100, q_precision
                    )
                    qty_take_2[2] = adjust(
                        order_size * take_volume_2[2] / 100, q_precision
                    )
                    qty_take_2[3] = adjust(
                        order_size * take_volume_2[3] / 100, q_precision
                    )
                    qty_take_2[4] = adjust(
                        order_size * take_volume_2[4] / 100, q_precision
                    )
                    qty_take_2[5] = adjust(
                        order_size * take_volume_2[5] / 100, q_precision
                    )
                    qty_take_2[6] = adjust(
                        order_size * take_volume_2[6] / 100, q_precision
                    )
                    qty_take_2[7] = adjust(
                        order_size * take_volume_2[7] / 100, q_precision
                    )
                    qty_take_2[8] = adjust(
                        order_size * take_volume_2[8] / 100, q_precision
                    )
                    qty_take_2[9] = adjust(
                        order_size * take_volume_2[9] / 100, q_precision
                    )
                    alert_open_long_2 = True

            # Trading logic (shorts)
            if position_type == 1:
                if high[i] >= stop_price[i]:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        600,
                        order_date,
                        time[i],
                        order_price,
                        stop_price[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    stop_price[i] = np.nan
                    take_price[:, i] = np.nan
                    qty_take_1[:] = np.nan
                    qty_take_2[:] = np.nan
                    stop_moved = False
                    grid_type = np.nan
                    alert_cancel = True

                if (stop_type == 1 and
                        change_upper_band[i] and
                        ((dst_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = adjust(
                        (dst_upper_band[i] * (100 + stop) / 100), 
                        p_precision
                    )
                    alert_short_new_stop = True
                elif (stop_type == 2 or stop_type == 3) and not stop_moved:
                    take = None

                    if grid_type == 0:
                        if (trail_stop == 4 and
                                low[i] <= take_price[3, i]):
                            take = take_price[3, i]
                        elif (trail_stop == 3 and
                                low[i] <= take_price[2, i]):
                            take = take_price[2, i]
                        elif (trail_stop == 2 and
                                low[i] <= take_price[1, i]):
                            take = take_price[1, i]
                        elif (trail_stop == 1 and
                                low[i] <= take_price[0, i]):
                            take = take_price[0, i]
                    elif grid_type == 1:
                        if (trail_stop == 9 and
                                low[i] <= take_price[8, i]):
                            take = take_price[8, i]
                        elif (trail_stop == 8 and
                                low[i] <= take_price[7, i]):
                            take = take_price[7, i]
                        elif (trail_stop == 7 and
                                low[i] <= take_price[6, i]):
                            take = take_price[6, i]
                        elif (trail_stop == 6 and
                                low[i] <= take_price[5, i]):
                            take = take_price[5, i]
                        elif (trail_stop == 5 and
                                low[i] <= take_price[4, i]):
                            take = take_price[4, i]
                        elif (trail_stop == 4 and
                                low[i] <= take_price[3, i]):
                            take = take_price[3, i]
                        elif (trail_stop == 3 and
                                low[i] <= take_price[2, i]):
                            take = take_price[2, i]
                        elif (trail_stop == 2 and
                                low[i] <= take_price[1, i]):
                            take = take_price[1, i]
                        elif (trail_stop == 1 and
                                low[i] <= take_price[0, i]):
                            take = take_price[0, i]

                    if take is not None:
                        stop_moved = True
                        stop_price[i] = adjust(
                            (take - order_price) * (trail_percent / 100)
                                + order_price,
                            p_precision
                        )
                        alert_short_new_stop = True
    
                if grid_type == 0:
                    if (not np.isnan(take_price[0, i]) and 
                            low[i] <= take_price[0, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            401,
                            order_date,
                            time[i],
                            order_price,
                            take_price[0, i],
                            qty_take_1[0],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[0], 8)
                        open_deals_log[0][4] = order_size
                        take_price[0, i] = np.nan
                        qty_take_1[0] = np.nan

                    if (not np.isnan(take_price[1, i]) and 
                            low[i] <= take_price[1, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            402,
                            order_date,
                            time[i],
                            order_price,
                            take_price[1, i],
                            qty_take_1[1],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[1], 8)
                        open_deals_log[0][4] = order_size
                        take_price[1, i] = np.nan
                        qty_take_1[1] = np.nan

                    if (not np.isnan(take_price[2, i]) and 
                            low[i] <= take_price[2, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            403,
                            order_date,
                            time[i],
                            order_price,
                            take_price[2, i],
                            qty_take_1[2],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[2], 8)
                        open_deals_log[0][4] = order_size
                        take_price[2, i] = np.nan
                        qty_take_1[2] = np.nan

                    if (not np.isnan(take_price[3, i]) and 
                            low[i] <= take_price[3, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            404,
                            order_date,
                            time[i],
                            order_price,
                            take_price[3, i],
                            qty_take_1[3],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_1[3], 8)
                        open_deals_log[0][4] = order_size
                        take_price[3, i] = np.nan
                        qty_take_1[3] = np.nan

                    if (not np.isnan(take_price[4, i]) and 
                            low[i] <= take_price[4, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            405,
                            order_date,
                            time[i],
                            order_price,
                            take_price[4, i],
                            round(qty_take_1[4], 8),
                            initial_capital
                        )
                        equity += pnl

                        open_deals_log[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[4, i] = np.nan
                        qty_take_1[4] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True
                elif grid_type == 1:
                    if (not np.isnan(take_price[0, i]) and 
                            low[i] <= take_price[0, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            401,
                            order_date,
                            time[i],
                            order_price,
                            take_price[0, i],
                            qty_take_2[0],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[0], 8)
                        open_deals_log[0][4] = order_size
                        take_price[0, i] = np.nan
                        qty_take_2[0] = np.nan

                    if (not np.isnan(take_price[1, i]) and 
                            low[i] <= take_price[1, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            402,
                            order_date,
                            time[i],
                            order_price,
                            take_price[1, i],
                            qty_take_2[1],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[1], 8)
                        open_deals_log[0][4] = order_size
                        take_price[1, i] = np.nan
                        qty_take_2[1] = np.nan

                    if (not np.isnan(take_price[2, i]) and 
                            low[i] <= take_price[2, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            403,
                            order_date,
                            time[i],
                            order_price,
                            take_price[2, i],
                            qty_take_2[2],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[2], 8)
                        open_deals_log[0][4] = order_size
                        take_price[2, i] = np.nan
                        qty_take_2[2] = np.nan

                    if (not np.isnan(take_price[3, i]) and 
                            low[i] <= take_price[3, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            404,
                            order_date,
                            time[i],
                            order_price,
                            take_price[3, i],
                            qty_take_2[3],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[3], 8)
                        open_deals_log[0][4] = order_size
                        take_price[3, i] = np.nan
                        qty_take_2[3] = np.nan

                    if (not np.isnan(take_price[4, i]) and 
                            low[i] <= take_price[4, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            405,
                            order_date,
                            time[i],
                            order_price,
                            take_price[4, i],
                            qty_take_2[4],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[4], 8)
                        open_deals_log[0][4] = order_size
                        take_price[4, i] = np.nan
                        qty_take_2[4] = np.nan

                    if (not np.isnan(take_price[5, i]) and 
                            low[i] <= take_price[5, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            406,
                            order_date,
                            time[i],
                            order_price,
                            take_price[5, i],
                            qty_take_2[5],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[5], 8)
                        open_deals_log[0][4] = order_size
                        take_price[5, i] = np.nan
                        qty_take_2[5] = np.nan

                    if (not np.isnan(take_price[6, i]) and 
                            low[i] <= take_price[6, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            407,
                            order_date,
                            time[i],
                            order_price,
                            take_price[6, i],
                            qty_take_2[6],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[6], 8)
                        open_deals_log[0][4] = order_size
                        take_price[6, i] = np.nan
                        qty_take_2[6] = np.nan

                    if (not np.isnan(take_price[7, i]) and 
                            low[i] <= take_price[7, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            408,
                            order_date,
                            time[i],
                            order_price,
                            take_price[7, i],
                            qty_take_2[7],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[7], 8)
                        open_deals_log[0][4] = order_size
                        take_price[7, i] = np.nan
                        qty_take_2[7] = np.nan

                    if (not np.isnan(take_price[8, i]) and 
                            low[i] <= take_price[8, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            409,
                            order_date,
                            time[i],
                            order_price,
                            take_price[8, i],
                            qty_take_2[8],
                            initial_capital
                        )
                        equity += pnl

                        order_size = round(order_size - qty_take_2[8], 8)
                        open_deals_log[0][4] = order_size
                        take_price[8, i] = np.nan
                        qty_take_2[8] = np.nan

                    if (not np.isnan(take_price[9, i]) and 
                            low[i] <= take_price[9, i]):
                        completed_deals_log, pnl = update_completed_deals_log(
                            completed_deals_log,
                            commission,
                            position_type,
                            order_signal,
                            410,
                            order_date,
                            time[i],
                            order_price,
                            take_price[9, i],
                            round(qty_take_2[9], 8),
                            initial_capital
                        )
                        equity += pnl

                        open_deals_log[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[9, i] = np.nan
                        qty_take_2[9] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True

            pre_entry_short = (
                (dst_upper_band[i] / close[i] - 1) * 100 > st_lower_band and
                (dst_upper_band[i] / close[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_short_upper_limit and
                rsi[i] > rsi_short_lower_limit and
                np.isnan(position_type) and
                (bb_rsi_lower[i] > bb_short_limit
                    if bb_filter else True) and
                last_pivot == 0 and
                (equity > min_capital) and
                (direction == 0 or direction == 2)
            )

            if pre_entry_short:
                if not np.isnan(pivot_HH) and not np.isnan(pivot_LL):
                    last_channel_range = (pivot_HH / pivot_LL - 1) * 100

                    for j in range(fibo_values.shape[0]):
                        price = pivot_HH - (pivot_HH - pivot_LL) * fibo_values[j]
                        fibo_levels[j] = price

            entry_short = (
                pre_entry_short and
                close[i] > fibo_levels[2] and
                close[i] <= fibo_levels[0]
            )

            if entry_short:
                position_type = 1
                order_signal = 200
                order_date = time[i]
                order_price = close[i]

                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                elif position_size_type == 1:
                    initial_position = (position_size * leverage)
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                    
                order_size = adjust(
                    order_size, q_precision
                )
                liquidation_price = adjust(
                    order_price * (1 + (1 / leverage)), p_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )

                if stop_type == 1 or stop_type == 2:
                    stop_price[i] = adjust(
                        dst_upper_band[i] * (100 + stop) / 100,
                        p_precision
                    )
                elif stop_type == 3:
                    stop_price[i] = adjust(
                        fibo_levels[0] * (100 + stop) / 100, p_precision
                    )

                if last_channel_range >= channel_range:
                    grid_type = 0

                    if close[i] <= fibo_levels[0] and close[i] > fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[2], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                    elif close[i] <= fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[7], p_precision
                        )

                    qty_take_1[0] = adjust(
                        order_size * take_volume_1[0] / 100, q_precision
                    )
                    qty_take_1[1] = adjust(
                        order_size * take_volume_1[1] / 100, q_precision
                    )
                    qty_take_1[2] = adjust(
                        order_size * take_volume_1[2] / 100, q_precision
                    )
                    qty_take_1[3] = adjust(
                        order_size * take_volume_1[3] / 100, q_precision
                    )
                    qty_take_1[4] = adjust(
                        order_size * take_volume_1[4] / 100, q_precision
                    )
                    alert_open_short_1 = True
                elif last_channel_range < channel_range:
                    grid_type = 1

                    if close[i] <= fibo_levels[0] and close[i] > fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[2], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[5, i] = adjust(
                            fibo_levels[7], p_precision
                        )
                        take_price[6, i] = adjust(
                            fibo_levels[8], p_precision
                        )
                        take_price[7, i] = adjust(
                            fibo_levels[9], p_precision
                        )
                        take_price[8, i] = adjust(
                            fibo_levels[10], p_precision
                        )
                        take_price[9, i] = adjust(
                            fibo_levels[11], p_precision
                        )
                    elif close[i] <= fibo_levels[1]:
                        take_price[0, i] = adjust(
                            fibo_levels[3], p_precision
                        )
                        take_price[1, i] = adjust(
                            fibo_levels[4], p_precision
                        )
                        take_price[2, i] = adjust(
                            fibo_levels[5], p_precision
                        )
                        take_price[3, i] = adjust(
                            fibo_levels[6], p_precision
                        )
                        take_price[4, i] = adjust(
                            fibo_levels[7], p_precision
                        )
                        take_price[5, i] = adjust(
                            fibo_levels[8], p_precision
                        )
                        take_price[6, i] = adjust(
                            fibo_levels[9], p_precision
                        )
                        take_price[7, i] = adjust(
                            fibo_levels[10], p_precision
                        )
                        take_price[8, i] = adjust(
                            fibo_levels[11], p_precision
                        )
                        take_price[9, i] = adjust(
                            fibo_levels[12], p_precision
                        )

                    qty_take_2[0] = adjust(
                        order_size * take_volume_2[0] / 100, q_precision
                    )
                    qty_take_2[1] = adjust(
                        order_size * take_volume_2[1] / 100, q_precision
                    )
                    qty_take_2[2] = adjust(
                        order_size * take_volume_2[2] / 100, q_precision
                    )
                    qty_take_2[3] = adjust(
                        order_size * take_volume_2[3] / 100, q_precision
                    )
                    qty_take_2[4] = adjust(
                        order_size * take_volume_2[4] / 100, q_precision
                    )
                    qty_take_2[5] = adjust(
                        order_size * take_volume_2[5] / 100, q_precision
                    )
                    qty_take_2[6] = adjust(
                        order_size * take_volume_2[6] / 100, q_precision
                    )
                    qty_take_2[7] = adjust(
                        order_size * take_volume_2[7] / 100, q_precision
                    )
                    qty_take_2[8] = adjust(
                        order_size * take_volume_2[8] / 100, q_precision
                    )
                    qty_take_2[9] = adjust(
                        order_size * take_volume_2[9] / 100, q_precision
                    )
                    alert_open_short_2 = True

        return (
            completed_deals_log,
            open_deals_log,
            stop_price,
            take_price,
            alert_cancel,
            alert_open_long_1,
            alert_open_long_2,
            alert_open_short_1,
            alert_open_short_2,
            alert_long_new_stop,
            alert_short_new_stop
        )

    def _trade(self, client: BaseExchangeClient) -> None:
        if self.alert_cancel:
            client.trade.cancel_all_orders(self.symbol)

        self.order_ids['stop_ids'] = client.trade.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )
        self.order_ids['limit_ids'] = client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_long_new_stop:
            client.trade.cancel_stop_orders(
                symbol=self.symbol,
                side='sell'
            )
            self.order_ids['stop_ids'] = client.trade.check_stop_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['stop_ids']
            )
            order_id = client.trade.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

        if self.alert_short_new_stop:
            client.trade.cancel_stop_orders(
                symbol=self.symbol,
                side='buy'
            )
            self.order_ids['stop_ids'] = client.trade.check_stop_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['stop_ids']
            )
            order_id = client.trade.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

        if self.alert_open_long_1:
            client.trade.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size']}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = client.trade.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][2]}%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][3]}%',
                price=self.take_price[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[4, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_long_2:
            client.trade.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size']}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = client.trade.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][2]}%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][3]}%',
                price=self.take_price[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][4]}%',
                price=self.take_price[4, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][5]}%',
                price=self.take_price[5, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][6]}%',
                price=self.take_price[6, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][7]}%',
                price=self.take_price[7, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][8]}%',
                price=self.take_price[8, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[9, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_short_1:
            client.trade.market_open_short(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size']}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = client.trade.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][2]}%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_1'][3]}%',
                price=self.take_price[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[4, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_short_2:
            client.trade.market_open_short(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size']}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )
            order_id = client.trade.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][2]}%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][3]}%',
                price=self.take_price[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][4]}%',
                price=self.take_price[4, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][5]}%',
                price=self.take_price[5, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][6]}%',
                price=self.take_price[6, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][7]}%',
                price=self.take_price[7, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2'][8]}%',
                price=self.take_price[8, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[9, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)