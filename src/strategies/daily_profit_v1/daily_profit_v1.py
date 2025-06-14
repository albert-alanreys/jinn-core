import numpy as np
import numba as nb

import src.core.quantklines as qk
from src.core.strategy.base_strategy import BaseStrategy
from src.core.utils.colors import encode_rgb
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
        "vwap_zone": 0.3,
        "vwap_close": False
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
        'vwap_zone': [0.2, 0.3, 0.4],
        'vwap_close': [True, False]
    }

    # For frontend
    indicator_options = {
        'SL': {'color': '#FF0000', 'lineWidth': 2},
        'TP #1': {'color': '#008000', 'lineWidth': 2},
        'TP #2': {'color': '#008000', 'lineWidth': 2},
        'ST ↑' : {'color': '#006400','lineWidth': 1, 'lineStyle': 2},
        'ST ↓' : {'color': '#8B0000','lineWidth': 1, 'lineStyle': 2},
        'VWAP': {'lineWidth': 3},
        'VWAP UB': {'lineWidth': 1},
        'VWAP LB': {'lineWidth': 1}
    }

    vwap_color_1 = encode_rgb(30, 144, 255)
    vwap_color_2 = encode_rgb(250, 128, 114)

    def __init__(self, client, all_params = None, opt_params = None) -> None:
        super().__init__(client, all_params, opt_params)

    def start(self, market_data) -> None:
        self.open_deals_log = np.full(5, np.nan)
        self.completed_deals_log = np.array([])

        self.deal_type = np.nan
        self.entry_signal = np.nan
        self.entry_date = np.nan
        self.entry_price = np.nan
        self.position_size = np.nan

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

        self.liquidation_price = np.nan

        self.stop_prices = np.full(self.time.shape[0], np.nan)
        self.moved_stop_price_1 = np.nan
        self.moved_stop_price_2 = np.nan

        self.take_prices = np.array(
            [
                np.full(self.time.shape[0], np.nan),
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.take_volumes = np.full(2, np.nan)

        self.dst_upper_band, self.dst_lower_band = qk.dst(
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

        self.vwap = qk.vwap(
            time=self.time,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )
        self.vwap_colors = np.empty(self.vwap.shape[0], dtype=np.float64)
        self.vwap_colors[0] = np.nan
        self.vwap_colors[1:] = np.where(
            self.vwap[1:] > self.vwap[:-1],
            self.vwap_color_1,
            self.vwap_color_2
        )

        self.vwap_upper_band = (
            self.vwap * (100 + self.params['vwap_zone']) / 100
        )
        self.vwap_lower_band = (
            self.vwap * (100 - self.params['vwap_zone']) / 100
        )

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_close_long = False
        self.alert_close_short = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False

        (
            self.open_deals_log,
            self.completed_deals_log,
            self.stop_prices,
            self.take_prices,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short,
            self.alert_long_new_stop,
            self.alert_short_new_stop
        ) = self._calculate(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['commission'],
            self.params['order_size_type'],
            self.params['order_size'],
            self.params['leverage'],
            self.params['stop'],
            self.params['trail_stop'],
            self.params['take_multiplier_1'],
            self.params['take_volume_1'],
            self.params['take_2'],
            self.params['take_multiplier_2'],
            self.params['take_volume_2'],
            self.params['stoch_rsi_upper_limit'],
            self.params['stoch_rsi_lower_limit'],
            self.params['vwap_close'],
            self.open_deals_log,
            self.completed_deals_log,
            self.deal_type,
            self.entry_signal,
            self.entry_date,
            self.entry_price,
            self.position_size,
            self.time,
            self.high,
            self.low,
            self.close,
            self.p_precision,
            self.q_precision,
            self.equity,
            self.liquidation_price,
            self.stop_prices,
            self.moved_stop_price_1,
            self.moved_stop_price_2,
            self.take_prices,
            self.take_volumes,
            self.dst_upper_band,
            self.dst_lower_band,
            self.stoch_rsi,
            self.vwap,
            self.vwap_upper_band,
            self.vwap_lower_band,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short,
            self.alert_long_new_stop,
            self.alert_short_new_stop
        )

        self.indicators = {
            'SL': {
                'options': self.indicator_options['SL'],
                'values': self.stop_prices
            },
            'TP #1': {
                'options': self.indicator_options['TP #1'],
                'values': self.take_prices[0]
            },
            'TP #2': {
                'options': self.indicator_options['TP #2'],
                'values': self.take_prices[1]
            },
            'ST ↑': {
                'options': self.indicator_options['ST ↑'],
                'values': self.dst_upper_band
            },
            'ST ↓': {
                'options': self.indicator_options['ST ↓'],
                'values': self.dst_lower_band
            },
            'VWAP': {
                'options': self.indicator_options['VWAP'],
                'values': self.vwap,
                'colors': self.vwap_colors
            },
            'VWAP UB': {
                'options': self.indicator_options['VWAP UB'],
                'values': self.vwap_upper_band,
                'colors': self.vwap_colors
            },
            'VWAP LB': {
                'options': self.indicator_options['VWAP LB'],
                'values': self.vwap_lower_band,
                'colors': self.vwap_colors
            }
        }

    @staticmethod
    @nb.jit(cache=True, nopython=True, nogil=True)
    def _calculate(
        direction: int,
        initial_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop: float,
        trail_stop: bool,
        take_multiplier_1: float,
        take_volume_1: float,
        take_2: bool,
        take_multiplier_2: float,
        take_volume_2: float,
        stoch_rsi_upper_limit: float,
        stoch_rsi_lower_limit: float,
        vwap_close: bool,
        open_deals_log: np.ndarray,
        completed_deals_log: np.ndarray,
        deal_type: float,
        entry_signal: float,
        entry_date: float,
        entry_price: float,
        position_size: float,
        time: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        p_precision: float,
        q_precision: float,
        equity: float,
        liquidation_price: float,
        stop_prices: np.ndarray,
        moved_stop_price_1: float,
        moved_stop_price_2: float,
        take_prices: np.ndarray,
        take_volumes: np.ndarray,
        dst_upper_band: np.ndarray,
        dst_lower_band: np.ndarray,
        stoch_rsi: np.ndarray,
        vwap: np.ndarray,
        vwap_upper_band: np.ndarray,
        vwap_lower_band: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_close_long: bool,
        alert_close_short: bool,
        alert_long_new_stop: bool,
        alert_short_new_stop: bool
    ) -> tuple:
        for i in range(2, time.shape[0]):
            stop_prices[i] = stop_prices[i - 1]
            take_prices[:, i] = take_prices[:, i - 1]

            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_close_long = False
            alert_close_short = False
            alert_long_new_stop = False
            alert_short_new_stop = False

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
                
                open_deals_log[:] = np.nan
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                position_size = np.nan
                liquidation_price = np.nan
                stop_prices[i] = np.nan
                take_prices[:, i] = np.nan
                take_volumes[:] = np.nan
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

                open_deals_log[:] = np.nan
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                position_size = np.nan
                liquidation_price = np.nan
                stop_prices[i] = np.nan
                take_prices[:, i] = np.nan
                take_volumes[:] = np.nan
                alert_cancel = True

            # Trading logic (longs)
            if deal_type == 0:
                if low[i] <= stop_prices[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        500,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_prices[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log[:] = np.nan
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    liquidation_price = np.nan
                    stop_prices[i] = np.nan
                    take_prices[:, i] = np.nan
                    take_volumes[:] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_prices[0, i])
                    and high[i] >= take_prices[0, i]
                ):
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        301,
                        entry_date,
                        time[i],
                        entry_price,
                        take_prices[0, i],
                        take_volumes[0],
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    position_size = round(position_size - take_volumes[0], 8)
                    open_deals_log[4] = position_size
                    take_prices[0, i] = np.nan
                    take_volumes[0] = np.nan

                    if trail_stop and stop_prices[i] < moved_stop_price_1:
                        stop_prices[i] = moved_stop_price_1
                        alert_long_new_stop = True

                if (
                    not np.isnan(take_prices[1, i])
                    and high[i] >= take_prices[1, i]
                ):
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        302,
                        entry_date,
                        time[i],
                        entry_price,
                        take_prices[1, i],
                        take_volumes[1],
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]
                    position_size = round(position_size - take_volumes[1], 8)

                    if position_size == 0:
                        open_deals_log[:] = np.nan
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        liquidation_price = np.nan
                        stop_prices[i] = np.nan
                        take_prices[:, i] = np.nan
                        take_volumes[:] = np.nan
                        alert_cancel = True
                    else:
                        open_deals_log[4] = position_size
                        take_prices[1, i] = np.nan
                        take_volumes[1] = np.nan

                        if trail_stop and stop_prices[i] < moved_stop_price_2:
                            stop_prices[i] = moved_stop_price_2
                            alert_long_new_stop = True

            if deal_type == 0:
                kline_ms = time[1] - time[0]
                day_1 = time[i] // 86400000
                day_2 = (time[i] + kline_ms) // 86400000

                is_exit_long = (
                    (vwap[i] < vwap[i - 1] if vwap_close else True) and
                    stoch_rsi[i] > stoch_rsi_upper_limit or
                    day_1 != day_2
                )

                if is_exit_long:
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

                    open_deals_log[:] = np.nan
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    liquidation_price = np.nan
                    stop_prices[i] = np.nan
                    take_prices[:, i] = np.nan
                    take_volumes[:] = np.nan
                    alert_close_long = True
                    alert_cancel = True

            is_entry_long = (
                np.isnan(deal_type) and
                (
                    high[i] > vwap_lower_band[i] and
                    high[i] < vwap_upper_band[i] or
                    low[i] > vwap_lower_band[i] and
                    low[i] < vwap_upper_band[i]
                ) and
                vwap[i] > vwap[i - 1] and
                stoch_rsi[i] < stoch_rsi_lower_limit and
                (direction == 0 or direction == 1) and
                not np.isnan(dst_lower_band[i])
            )

            if is_entry_long:
                deal_type = 0
                entry_signal = 100
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
                stop_prices[i] = adjust(
                    dst_lower_band[i] * (100 - stop) / 100, p_precision
                )
                moved_stop_price_1 = entry_price

                stop_distance = abs((stop_prices[i] / entry_price - 1) * 100)
                take_distance_1 = stop_distance * take_multiplier_1
                take_prices[0, i] = adjust(
                    entry_price * (100 + take_distance_1) / 100,
                    p_precision
                )
                moved_stop_price_1 = take_prices[0, i]

                if take_2:
                    take_distance_2 = take_distance_1 * take_multiplier_2
                    take_prices[1, i] = adjust(
                        entry_price * (100 + take_distance_2) / 100,
                        p_precision
                    )

                position_size = adjust(
                    position_size, q_precision
                )
                take_volumes[0] = adjust(
                    position_size * take_volume_1 / 100, q_precision
                )
                take_volumes[1] = adjust(
                    position_size * take_volume_2 / 100, q_precision
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
                if high[i] >= stop_prices[i]:
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        600,
                        entry_date,
                        time[i],
                        entry_price,
                        stop_prices[i],
                        position_size,
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    open_deals_log[:] = np.nan
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    liquidation_price = np.nan
                    stop_prices[i] = np.nan
                    take_prices[:, i] = np.nan
                    take_volumes[:] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_prices[0, i])
                    and low[i] <= take_prices[0, i]
                ):
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        401,
                        entry_date,
                        time[i],
                        entry_price,
                        take_prices[0, i],
                        take_volumes[0],
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]

                    position_size = round(position_size - take_volumes[0], 8)
                    open_deals_log[4] = position_size
                    take_prices[0, i] = np.nan
                    take_volumes[0] = np.nan

                    if trail_stop and stop_prices[i] > moved_stop_price_1:
                        stop_prices[i] = moved_stop_price_1
                        alert_short_new_stop = True
                if (
                    not np.isnan(take_prices[1, i])
                    and low[i] <= take_prices[1, i]
                ):
                    log_entry = create_log_entry(
                        completed_deals_log,
                        commission,
                        deal_type,
                        entry_signal,
                        402,
                        entry_date,
                        time[i],
                        entry_price,
                        take_prices[1, i],
                        take_volumes[1],
                        initial_capital
                    )
                    completed_deals_log = np.concatenate(
                        (completed_deals_log, log_entry)
                    )
                    equity += log_entry[8]
                    position_size = round(position_size - take_volumes[1], 8)

                    if position_size == 0:
                        open_deals_log[:] = np.nan
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        liquidation_price = np.nan
                        stop_prices[i] = np.nan
                        take_prices[:, i] = np.nan
                        take_volumes[:] = np.nan
                        alert_cancel = True
                    else:
                        open_deals_log[4] = position_size
                        take_prices[1, i] = np.nan
                        take_volumes[1] = np.nan

                        if trail_stop and stop_prices[i] > moved_stop_price_2:
                            stop_prices[i] = moved_stop_price_2
                            alert_short_new_stop = True

            if deal_type == 1:
                kline_ms = time[1] - time[0]
                day_1 = time[i] // 86400000
                day_2 = (time[i] + kline_ms) // 86400000

                is_exit_short = (
                    (vwap[i] >= vwap[i - 1] if vwap_close else True) and
                    stoch_rsi[i] < stoch_rsi_lower_limit or
                    day_1 != day_2
                )

                if is_exit_short:
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

                    open_deals_log[:] = np.nan
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    position_size = np.nan
                    liquidation_price = np.nan
                    stop_prices[i] = np.nan
                    take_prices[:, i] = np.nan
                    take_volumes[:] = np.nan
                    alert_close_short = True
                    alert_cancel = True

            is_entry_short = (
                np.isnan(deal_type) and
                (
                    high[i] > vwap_lower_band[i] and
                    high[i] < vwap_upper_band[i] or
                    low[i] > vwap_lower_band[i] and
                    low[i] < vwap_upper_band[i]
                ) and
                vwap[i] < vwap[i - 1] and
                stoch_rsi[i] > stoch_rsi_upper_limit and
                (direction == 0 or direction == 2) and
                not np.isnan(dst_upper_band[i])
            )

            if is_entry_short:
                deal_type = 1
                entry_signal = 200
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
                stop_prices[i] = adjust(
                    dst_upper_band[i] * (100 + stop) / 100, p_precision
                )
                moved_stop_price_1 = entry_price

                stop_distance = abs((stop_prices[i] / entry_price - 1) * 100)
                take_distance_1 = stop_distance * take_multiplier_1
                take_prices[0, i] = adjust(
                    entry_price * (100 - take_distance_1) / 100,
                    p_precision
                )
                moved_stop_price_2 = take_prices[0, i]

                if take_2:
                    take_distance_2 = take_distance_1 * take_multiplier_2
                    take_prices[1, i] = adjust(
                        entry_price * (100 - take_distance_2) / 100,
                        p_precision
                    )

                position_size = adjust(
                    position_size, q_precision
                )
                take_volumes[0] = adjust(
                    position_size * take_volume_1 / 100, q_precision
                )
                take_volumes[1] = adjust(
                    position_size * take_volume_2 / 100, q_precision
                )

                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_open_short = True

        return (
            open_deals_log,
            completed_deals_log,
            stop_prices,
            take_prices,
            alert_cancel,
            alert_open_long,
            alert_open_short,
            alert_close_long,
            alert_close_short,
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
            self.client.cancel_stop_orders(
                symbol=self.symbol,
                side='Sell'
            )
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
            self.client.cancel_stop_orders(
                symbol=self.symbol,
                side='Buy'
            )
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
                size=f'{self.params['take_volume_1']}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_long(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2']}%',
                price=self.take_price[1, -1],
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
                size=f'{self.params['take_volume_1']}%',
                price=self.take_price[0, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_close_short(
                symbol=self.symbol,
                size=f'{self.params['take_volume_2']}%',
                price=self.take_price[1, -1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        self.cache.save(self.symbol, self.order_ids)