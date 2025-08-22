from random import randint
from typing import TYPE_CHECKING

import numpy as np
import numba as nb

import src.core.quantklines as qk
from src.infrastructure.exchanges.enums import Interval
from src.shared.constants import colors
from src.shared.utils import adjust
from .strategy import BaseStrategy
from .utils import update_completed_deals_log

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient


class ExampleV2(BaseStrategy):
    # Strategy parameters
    params = {
        'position_size': 90.0, 
        'min_capital': 100.0,
        'stop_type': 1,
        'trail_stop': 1,
        'stop': 2.0,
        'trail_percent': 30.0,
        'take_percent': [2.0, 4.0, 6.0],
        'take_volume': [10.0, 10.0, 50.0],
        'st_atr_period': 6,
        'st_factor': 24.6,
        'st_upper_band': 5.8,
        'st_lower_band': 2.9,
        'rsi_length': 6,
        'rsi_long_upper_limit': 29.0,
        'rsi_long_lower_limit': 28.0,
        'rsi_short_upper_limit': 69.0,
        'rsi_short_lower_limit': 58.0,
        'bb_filter': False,
        'ma_length': 22,
        'bb_mult': 2.7,
        'bb_long_limit': 24.0,
        'bb_short_limit': 67.0,
        'adx_filter': False,
        'adx_length': 6,
        'di_length': 14,
        'adx_long_upper_limit': 44.0,
        'adx_long_lower_limit': 28.0,
        'adx_short_upper_limit': 77.0,
        'adx_short_lower_limit': 1.0,
        'feeds': {
            'klines': {
                'HTF': ['symbol', Interval.DAY_1],
                'LTF': ['symbol', Interval.MIN_1],
            }
        }
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_type': [1, 2],
        'trail_stop': [1, 2],
        'stop': [i / 10 for i in range(1, 31)],
        'trail_percent': [float(i) for i in range(0, 55, 1)],
        'take_percent': [
            [
                randint(12, 46) / 10,
                randint(48, 86) / 10,
                randint(88, 146) / 10
            ] for _ in range(100)
        ],
        'take_volume': [
            [33.33, 33.33, 33.34],
            [60.0, 30.0, 10.0],
            [10.0, 30.0, 60.0],
            [20.0, 50.0, 30.0],
            [40.0, 40.0, 20.0],
            [20.0, 50.0, 30.0],
            [70.0, 20.0, 10.0],
            [10.0, 20.0, 70.0],
            [50.0, 30.0, 20.0],
            [20.0, 30.0, 50.0],
            [50.0, 30.0, 20.0],
            [20.0, 30.0, 50.0],
            [40.0, 20.0, 40.0],
            [20.0, 50.0, 30.0],
            [60.0, 20.0, 20.0],
            [20.0, 20.0, 60.0],
            [25.0, 40.0, 35.0],
            [50.0, 30.0, 20.0],
            [20.0, 60.0, 20.0],
            [10.0, 40.0, 50.0]
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

    # Frontend rendering settings
    indicator_options = {
        'HTF': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON
        },
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
        'Volume': {
            'pane': 1,
            'type': 'histogram'
        },
        '+DI': {
            'pane': 2,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 1
        },
        '-DI': {
            'pane': 2,
            'type': 'line',
            'color': colors.CRIMSON,
            'lineWidth': 1
        },
        'ADX': {
            'pane': 2,
            'type': 'line',
            'color': colors.DEEP_SKY_BLUE,
            'lineWidth': 1
        },
    }

    volume_color_1 = colors.PEACOCK_GREEN
    volume_color_2 = colors.CHERRY_RED

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)

    def calculate(self, market_data) -> None:
        # Initialize base variables from market data
        super().init_variables(market_data)

        # Initialize strategy-specific arrays
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )

        # Position tracking variables
        self.liquidation_price = np.nan
        self.qty_take = np.full(5, np.nan)
        self.stop_moved = False

        # Calculate technical indicators
        self.dst = qk.dst(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['st_factor'],
            atr_length=self.params['st_atr_period']
        )
        self.upper_band_change = qk.change(
            source=self.dst[0],
            length=1
        )
        self.lower_band_change = qk.change(
            source=self.dst[1],
            length=1
        )
        self.rsi = qk.rsi(
            source=self.close,
            length=self.params['rsi_length']
        )

        if self.params['bb_filter']:
            self.bb_rsi = qk.bb(
                source=self.rsi,
                length=self.params['ma_length'],
                mult=self.params['bb_mult']
            )
        else:
            self.bb_rsi = np.full(self.time.shape[0], np.nan)

        self.dmi = qk.dmi(
            high=self.high,
            low=self.low,
            close=self.close,
            di_length=self.params['di_length'],
            adx_length=self.params['adx_length']
        )
        self.adx = self.dmi[2]

        # Additional data
        self.htf_close = np.full(self.time.shape[0], np.nan)

        if len(self.feeds['klines']['HTF']['close'].shape) == 1:
            self.htf_close = self.feeds['klines']['HTF']['close']

        # Alert flags for signals
        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False

        # Graphics
        self.volume_colors = np.where(
            self.close >= self.open,
            self.volume_color_1,
            self.volume_color_2
        )

        # Main calculation loop (Numba-optimized)
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
            self.position_type,
            self.order_signal,
            self.order_date,
            self.order_price,
            self.liquidation_price,
            self.take_price,
            self.stop_price,
            self.order_size,
            self.qty_take,
            self.stop_moved,
            self.dst[0],
            self.dst[1],
            self.upper_band_change,
            self.lower_band_change,
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
            'HTF': {
                'options': self.indicator_options['HTF'],
                'values': self.htf_close
            },
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
            'Volume': {
                'options': self.indicator_options['Volume'],
                'values': self.volume,
                'colors': self.volume_colors
            },
            '+DI': {
                'options': self.indicator_options['+DI'],
                'values': self.dmi[0]
            },
            '-DI': {
                'options': self.indicator_options['-DI'],
                'values': self.dmi[1]
            },
            'ADX': {
                'options': self.indicator_options['ADX'],
                'values': self.dmi[2]
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
        position_type: float,
        order_signal: float,
        order_date: float,
        order_price: float,
        liquidation_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        order_size: float,
        qty_take: np.ndarray,
        stop_moved: int,
        dst_upper_band: np.ndarray,
        dst_lower_band: np.ndarray,
        upper_band_change: np.ndarray,
        lower_band_change: np.ndarray,
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
        for i in range(1, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_price[:, i] = take_price[:, i - 1]

            # Reset alerts
            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_long_new_stop = False
            alert_short_new_stop = False

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

                # Reset variables
                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                take_price[:, i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                qty_take[:] = np.nan
                stop_moved = False
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
                take_price[:, i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                qty_take[:] = np.nan
                stop_moved = False
                alert_cancel = True

            # Long position management
            if position_type == 0:
                # Stop loss check
                if low[i] <= stop_price[i]:
                    # Close position and log deal
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
                    take_price[:, i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    qty_take[:] = np.nan
                    stop_moved = False
                    alert_cancel = True

                if (stop_type == 1 and
                        lower_band_change[i] and
                        ((dst_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = adjust(
                        dst_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                    alert_long_new_stop = True
                elif stop_type == 2 and not stop_moved:
                    take = None

                    if (trail_stop == 2 and
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

                # Take profit checks
                if not np.isnan(take_price[0, i]) and high[i] >= take_price[0, i]:
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
                        qty_take[0],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - qty_take[0], 8)
                    open_deals_log[0][4] = order_size
                    take_price[0, i] = np.nan
                    qty_take[0] = np.nan

                if not np.isnan(take_price[1, i]) and high[i] >= take_price[1, i]:
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
                        qty_take[1],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - qty_take[1], 8)
                    open_deals_log[0][4] = order_size
                    take_price[1, i] = np.nan
                    qty_take[1] = np.nan

                if not np.isnan(take_price[2, i]) and high[i] >= take_price[2, i]:
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
                        round(qty_take[2], 8),
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    order_size = np.nan
                    take_price[2, i] = np.nan
                    qty_take[2] = np.nan
                    stop_price[i] = np.nan
                    stop_moved = False
                    alert_cancel = True

            # Entry signal logic
            entry_long = (
                (close[i] / dst_lower_band[i] - 1) * 100 > st_lower_band and
                (close[i] / dst_lower_band[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_long_upper_limit and
                rsi[i] > rsi_long_lower_limit and
                np.isnan(position_type) and
                (bb_rsi_upper[i] < bb_long_limit
                    if bb_filter else True) and
                (adx[i] < adx_long_upper_limit and
                    adx[i] > adx_long_lower_limit
                    if adx_filter else True) and
                (equity > min_capital) and
                (direction == 0 or direction == 1)
            )

            if entry_long:
                # Initialize long position
                position_type = 0
                order_signal = 100
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
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                    
                order_date = time[i]
                liquidation_price = adjust(
                    order_price * (1 - (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    dst_lower_band[i] * (100 - stop) / 100, p_precision
                )
                take_price[0, i] = adjust(
                    close[i] * (100 + take_percent[0]) / 100, p_precision
                )
                take_price[1, i] = adjust(
                    close[i] * (100 + take_percent[1]) / 100, p_precision
                )
                take_price[2, i] = adjust(
                    close[i] * (100 + take_percent[2]) / 100, p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                qty_take[0] = adjust(
                    order_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = adjust(
                    order_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = adjust(
                    order_size * take_volume[2] / 100, q_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )
                alert_open_long = True

            # Short position management
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
                    take_price[:, i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    qty_take[:] = np.nan
                    stop_moved = False
                    alert_cancel = True 

                if (stop_type == 1 and
                        upper_band_change[i] and
                        ((dst_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = adjust(
                        (dst_upper_band[i] * (100 + stop) / 100), 
                        p_precision
                    )
                    alert_short_new_stop = True
                elif stop_type == 2 and not stop_moved:
                    take = None

                    if (trail_stop == 2 and
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

                if not np.isnan(take_price[0, i]) and low[i] <= take_price[0, i]:
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
                        qty_take[0],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - qty_take[0], 8)
                    open_deals_log[0][4] = order_size
                    take_price[0, i] = np.nan
                    qty_take[0] = np.nan

                if not np.isnan(take_price[1, i]) and low[i] <= take_price[1, i]:
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
                        qty_take[1],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - qty_take[1], 8)
                    open_deals_log[0][4] = order_size
                    take_price[1, i] = np.nan
                    qty_take[1] = np.nan         

                if not np.isnan(take_price[2, i]) and low[i] <= take_price[2, i]:
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
                        round(qty_take[2], 8),
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    order_size = np.nan
                    take_price[2, i] = np.nan
                    qty_take[2] = np.nan
                    stop_price[i] = np.nan
                    stop_moved = False
                    alert_cancel = True

            entry_short = (
                (dst_upper_band[i] / close[i] - 1) * 100 > st_lower_band and
                (dst_upper_band[i] / close[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_short_upper_limit and
                rsi[i] > rsi_short_lower_limit and
                np.isnan(position_type) and
                (bb_rsi_lower[i] > bb_short_limit
                    if bb_filter else True) and
                (adx[i] < adx_short_upper_limit and
                    adx[i] > adx_short_lower_limit
                    if adx_filter else True) and
                (equity > min_capital) and
                (direction == 0 or direction == 2)
            )

            if entry_short:
                position_type = 1
                order_signal = 200
                order_price = close[i]

                if position_size_type == 0:
                    initial_position = (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                elif position_size_type == 1:
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )

                order_date = time[i]
                liquidation_price = adjust(
                    order_price * (1 + (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    dst_upper_band[i] * (100 + stop) / 100, p_precision
                )
                take_price[0, i] = adjust(
                    close[i] * (100 - take_percent[0]) / 100, p_precision
                )
                take_price[1, i] = adjust(
                    close[i] * (100 - take_percent[1]) / 100, p_precision
                )
                take_price[2, i] = adjust(
                    close[i] * (100 - take_percent[2]) / 100, p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                qty_take[0] = adjust(
                    order_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = adjust(
                    order_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = adjust(
                    order_size * take_volume[2] / 100, q_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
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

    def _trade(self, client: 'BaseExchangeClient') -> None:
        # Cancel all orders if needed
        if self.alert_cancel:
            client.trade.cancel_all_orders(self.symbol)

         # Check order status
        self.order_ids['stop_ids'] = client.trade.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )
        self.order_ids['limit_ids'] = client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        # Update stop loss
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

        # Open long position
        if self.alert_open_long:
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
                size=f'{self.params['take_volume'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_short:
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
                size=f'{self.params['take_volume'][0]}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume'][1]}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)