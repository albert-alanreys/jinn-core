import numpy as np
import numba as nb

from . import (
    BaseStrategy,
    BaseExchangeClient,
    adjust,
    colors,
    quantklines,
    update_completed_deals_log
)


class NuggetV5(BaseStrategy):
    # --- Strategy Configuration ---
    # Default parameter values for backtesting and live trading
    params = {
        'min_capital': 100.0,
        'stop': 2.8,
        'atr_length': 14,
        'take_factor_1': 3.0,
        'take_factor_2': 4.0,
        'take_factor_3': 5.0,
        'take_factor_4': 6.0,
        'take_factor_5': 7.0,
        'take_volume_1': 10.0,
        'take_volume_2': 10.0,
        'take_volume_3': 50.0,
        'take_volume_4': 20.0,
        'take_volume_5': 10.0,
        'st_atr_period': 6,
        'st_factor': 24.6,
        'st_upper_limit': 5.8,
        'st_lower_limit': 2.9,
        'k_length': 14,
        'd_length': 3,
        'k_d_long_limit': 20.0,
        'k_d_short_limit': 80.0,
        'adx_filter': False,
        'di_length': 14,
        'adx_length': 6,
        'adx_long_upper_limit': 44.0,
        'adx_long_lower_limit': 28.0,
        'adx_short_upper_limit': 77.0,
        'adx_short_lower_limit': 1.0,
    }

    # --- Optimization Space ---
    # Parameter ranges for hyperparameter optimization
    opt_params = {
        'stop': [i / 10 for i in range(1, 31)],
        'atr_length': [i for i in range(1, 21)],
        'take_factor_1': [i / 10 for i in range(20, 71, 5)],
        'take_factor_2': [i / 10 for i in range(70, 111, 5)],
        'take_factor_3': [i / 10 for i in range(110, 171, 5)],
        'take_factor_4': [i / 10 for i in range(170, 221, 5)],
        'take_factor_5': [i / 10 for i in range(220, 311, 5)],
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
        'adx_short_lower_limit': [float(i) for i in range(1, 69)],
    }

    # --- UI/UX Configuration ---
    # Human-readable labels for frontend parameter display
    param_labels = {
        'min_capital': 'Min Capital',
        'stop': 'Stop Loss (%)',
        'atr_length': 'ATR Length',
        'take_factor_1': 'TP Factor 1',
        'take_factor_2': 'TP Factor 2',
        'take_factor_3': 'TP Factor 3',
        'take_factor_4': 'TP Factor 4',
        'take_factor_5': 'TP Factor 5',
        'take_volume_1': 'TP Volume 1',
        'take_volume_2': 'TP Volume 2',
        'take_volume_3': 'TP Volume 3',
        'take_volume_4': 'TP Volume 4',
        'take_volume_5': 'TP Volume 5',
        'st_atr_period': 'ST ATR Period',
        'st_factor': 'ST Factor',
        'st_upper_limit': 'ST Upper Limit',
        'st_lower_limit': 'ST Lower Limit',
        'k_length': 'Stoch K Length',
        'd_length': 'Stoch D Length',
        'k_d_long_limit': 'Stoch Long Limit',
        'k_d_short_limit': 'Stoch Short Limit',
        'adx_filter': 'ADX Filter',
        'di_length': 'DI Length',
        'adx_length': 'ADX Length',
        'adx_long_upper_limit': 'ADX Long Upper',
        'adx_long_lower_limit': 'ADX Long Lower',
        'adx_short_upper_limit': 'ADX Short Upper',
        'adx_short_lower_limit': 'ADX Short Lower',
    }

    # --- Visualization Settings ---
    # Chart styling configuration for technical indicators
    indicator_options = {
        'SL': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON,
            'lineWidth': 2,
        },
        'TP #1': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2,
        },
        'TP #2': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2,
        },
        'TP #3': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2,
        },
        'TP #4': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2,
        },
        'TP #5': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2,
        },
    }

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)

    def calculate(self) -> None:
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_prices = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.take_factors = np.array([
            self.params['take_factor_1'],
            self.params['take_factor_2'],
            self.params['take_factor_3'],
            self.params['take_factor_4'],
            self.params['take_factor_5']
        ])
        self.liquidation_price = np.nan

        self.take_volumes = np.array([
            self.params['take_volume_1'],
            self.params['take_volume_2'],
            self.params['take_volume_3'],
            self.params['take_volume_4'],
            self.params['take_volume_5']
        ])
        self.take_quantities = np.full(5, np.nan)

        self.atr = quantklines.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_length']
        )
        self.dst = quantklines.dst(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['st_factor'],
            atr_length=self.params['st_atr_period']
        )
        self.st_upper_band_changed = quantklines.change(
            source=self.dst[0],
            length=1
        )
        self.st_lower_band_changed = quantklines.change(
            source=self.dst[1],
            length=1
        )
        self.k = quantklines.stoch(
            source=self.close,
            high=self.high,
            low=self.low,
            length=self.params['k_length']
        )
        self.d = quantklines.sma(
            source=self.k,
            length=self.params['d_length']
        )

        if self.params['adx_filter']:
            dmi = quantklines.dmi(
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
            self.take_prices,
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
            self.params['stop'],
            self.params['st_upper_limit'],
            self.params['st_lower_limit'],
            self.params['k_d_long_limit'],
            self.params['k_d_short_limit'],
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
            self.order_price,
            self.order_date,
            self.order_size,
            self.stop_price,
            self.take_prices,
            self.take_factors,
            self.liquidation_price,
            self.take_volumes,
            self.take_quantities,
            self.atr,
            self.dst[0],
            self.dst[1],
            self.st_upper_band_changed,
            self.st_lower_band_changed,
            self.k,
            self.d,
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
                'values': self.stop_price,
            },
            'TP #1': {
                'options': self.indicator_options['TP #1'],
                'values': self.take_prices[0],
            },
            'TP #2': {
                'options': self.indicator_options['TP #2'],
                'values': self.take_prices[1],
            },
            'TP #3': {
                'options': self.indicator_options['TP #3'],
                'values': self.take_prices[2],
            },
            'TP #4': {
                'options': self.indicator_options['TP #4'],
                'values': self.take_prices[3],
            },
            'TP #5': {
                'options': self.indicator_options['TP #5'],
                'values': self.take_prices[4],
            },
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
        stop: float,
        st_upper_limit: float,
        st_lower_limit: float,
        k_d_long_limit: float,
        k_d_short_limit: float,
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
        order_price: float,
        order_date: float,
        order_size: float,
        stop_price: np.ndarray,
        take_prices: np.ndarray,
        take_factors: np.ndarray,
        liquidation_price: float,
        take_volumes: np.ndarray,
        take_quantities: np.ndarray,
        atr: np.ndarray,
        dst_upper_band: np.ndarray,
        dst_lower_band: np.ndarray,
        st_upper_band_changed: np.ndarray,
        st_lower_band_changed: np.ndarray,
        k: np.ndarray,
        d: np.ndarray,
        adx: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_long_new_stop: bool,
        alert_short_new_stop: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_prices[:, i] = take_prices[:, i - 1]

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
                
                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                take_prices[:, i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                take_quantities[:] = np.nan
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
                take_prices[:, i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                take_quantities[:] = np.nan
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
                    take_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    take_quantities[:] = np.nan
                    alert_cancel = True

                if (st_lower_band_changed[i] and
                        ((dst_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = adjust(
                        dst_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                    alert_long_new_stop = True

                if (
                    not np.isnan(take_prices[0, i]) and
                    high[i] >= take_prices[0, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        301,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[0, i],
                        take_quantities[0],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[0], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[0, i] = np.nan
                    take_quantities[0] = np.nan

                if (
                    not np.isnan(take_prices[1, i]) and
                    high[i] >= take_prices[1, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        302,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[1, i],
                        take_quantities[1],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[1], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[1, i] = np.nan
                    take_quantities[1] = np.nan

                if (
                    not np.isnan(take_prices[2, i]) and
                    high[i] >= take_prices[2, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        303,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[2, i],
                        take_quantities[2],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[2], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[2, i] = np.nan
                    take_quantities[2] = np.nan

                if (
                    not np.isnan(take_prices[3, i]) and
                    high[i] >= take_prices[3, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        304,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[3, i],
                        take_quantities[3],
                        initial_capital
                    ) 
                    equity += pnl

                    order_size = round(order_size - take_quantities[3], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[3, i] = np.nan
                    take_quantities[3] = np.nan

                if (
                    not np.isnan(take_prices[4, i]) and
                    high[i] >= take_prices[4, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        305,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[4, i],
                        round(take_quantities[4], 8),
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    order_size = np.nan
                    take_prices[4, i] = np.nan
                    take_quantities[4] = np.nan
                    stop_price[i] = np.nan
                    alert_cancel = True

            entry_long = (
                (close[i] / dst_lower_band[i] - 1) * 100 > st_lower_limit and
                (close[i] / dst_lower_band[i] - 1) * 100 < st_upper_limit and
                k[i] < k_d_long_limit and
                d[i] < k_d_long_limit and
                np.isnan(position_type) and
                (adx[i] < adx_long_upper_limit and
                    adx[i] > adx_long_lower_limit
                    if adx_filter else True) and
                (equity > min_capital) and
                (direction == 0 or direction == 1)
            )

            if entry_long:
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
                take_prices[0, i] = adjust(
                    close[i] + take_factors[0] * atr[i], p_precision
                )
                take_prices[1, i] = adjust(
                    close[i] + take_factors[1] * atr[i], p_precision
                )
                take_prices[2, i] = adjust(
                    close[i] + take_factors[2] * atr[i], p_precision
                )
                take_prices[3, i] = adjust(
                    close[i] + take_factors[3] * atr[i], p_precision
                )
                take_prices[4, i] = adjust(
                    close[i] + take_factors[4] * atr[i], p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                take_quantities[0] = adjust(
                    order_size * take_volumes[0] / 100, q_precision
                )
                take_quantities[1] = adjust(
                    order_size * take_volumes[1] / 100, q_precision
                )
                take_quantities[2] = adjust(
                    order_size * take_volumes[2] / 100, q_precision
                )
                take_quantities[3] = adjust(
                    order_size * take_volumes[3] / 100, q_precision
                )
                take_quantities[4] = adjust(
                    order_size * take_volumes[4] / 100, q_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )
                alert_open_long = True

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
                    take_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    take_quantities[:] = np.nan
                    alert_cancel = True 

                if (st_upper_band_changed[i] and
                        ((dst_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = adjust(
                        (dst_upper_band[i] * (100 + stop) / 100), 
                        p_precision
                    )
                    alert_short_new_stop = True

                if (
                    not np.isnan(take_prices[0, i]) and
                    low[i] <= take_prices[0, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        401,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[0, i],
                        take_quantities[0],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[0], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[0, i] = np.nan
                    take_quantities[0] = np.nan

                if (
                    not np.isnan(take_prices[1, i]) and
                    low[i] <= take_prices[1, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        402,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[1, i],
                        take_quantities[1],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[1], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[1, i] = np.nan
                    take_quantities[1] = np.nan      

                if (
                    not np.isnan(take_prices[2, i]) and
                    low[i] <= take_prices[2, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        403,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[2, i],
                        take_quantities[2],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[2], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[2, i] = np.nan
                    take_quantities[2] = np.nan

                if (
                    not np.isnan(take_prices[3, i]) and
                    low[i] <= take_prices[3, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        404,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[3, i],
                        take_quantities[3],
                        initial_capital
                    )
                    equity += pnl

                    order_size = round(order_size - take_quantities[3], 8)
                    open_deals_log[0][4] = order_size
                    take_prices[3, i] = np.nan
                    take_quantities[3] = np.nan     

                if (
                    not np.isnan(take_prices[4, i]) and
                    low[i] <= take_prices[4, i]
                ):
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        405,
                        order_date,
                        time[i],
                        order_price,
                        take_prices[4, i],
                        round(take_quantities[4], 8),
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    order_size = np.nan
                    take_prices[4, i] = np.nan
                    take_quantities[4] = np.nan
                    stop_price[i] = np.nan
                    alert_cancel = True

            entry_short = (
                (dst_upper_band[i] / close[i] - 1) * 100 > st_lower_limit and
                (dst_upper_band[i] / close[i] - 1) * 100 < st_upper_limit and
                k[i] > k_d_short_limit and
                d[i] > k_d_short_limit and
                np.isnan(position_type) and
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
                take_prices[0, i] = adjust(
                    close[i] - take_factors[0] * atr[i], p_precision
                )
                take_prices[1, i] = adjust(
                    close[i] - take_factors[1] * atr[i], p_precision
                )
                take_prices[2, i] = adjust(
                    close[i] - take_factors[2] * atr[i], p_precision
                )
                take_prices[3, i] = adjust(
                    close[i] - take_factors[3] * atr[i], p_precision
                )
                take_prices[4, i] = adjust(
                    close[i] - take_factors[4] * atr[i], p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                take_quantities[0] = adjust(
                    order_size * take_volumes[0] / 100, q_precision
                )
                take_quantities[1] = adjust(
                    order_size * take_volumes[1] / 100, q_precision
                )
                take_quantities[2] = adjust(
                    order_size * take_volumes[2] / 100, q_precision
                )
                take_quantities[3] = adjust(
                    order_size * take_volumes[3] / 100, q_precision
                )
                take_quantities[4] = adjust(
                    order_size * take_volumes[4] / 100, q_precision
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
            take_prices,
            stop_price,
            alert_cancel,
            alert_open_long,
            alert_open_short,
            alert_long_new_stop,
            alert_short_new_stop
        )

    def trade(self, client: BaseExchangeClient) -> None:
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
                size=f'{self.take_volumes[0]}%',
                price=self.take_prices[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.take_volumes[1]}%',
                price=self.take_prices[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.take_volumes[2]}%',
                price=self.take_prices[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size=f'{self.take_volumes[3]}%',
                price=self.take_prices[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_prices[4, -1],
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
                size=f'{self.take_volumes[0]}%',
                price=self.take_prices[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.take_volumes[1]}%',
                price=self.take_prices[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.take_volumes[2]}%',
                price=self.take_prices[2, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size=f'{self.take_volumes[3]}%',
                price=self.take_prices[3, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_prices[4, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)