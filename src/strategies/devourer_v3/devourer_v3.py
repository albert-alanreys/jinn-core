import numpy as np
import numba as nb

import src.core.lib.ta as ta
from src.core.strategy.base_strategy import BaseStrategy


class DevourerV3(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes

    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    # direction: 0 - "all", 1 — "longs", 2 — "shorts"
    # order_size_type: 0 — "PERCENT", 1 — "CURRENCY"

    params = {
        "margin_type": 0,
        "direction": 0,
        "initial_capital": 10000.0,
        "commission": 0.05,
        "order_size_type": 0,
        "order_size": 100.0,
        "leverage": 1,
        "stop_atr_p2": 0.5,
        "stop_atr_p3": 1.0,
        "take_atr_p3": 3.0,
        "fast_len_p1": 12,
        "slow_len_p1": 26,
        "sig_len_p1": 14,
        "k_len_p1": 14,
        "d_len_p1": 3,
        "kd_limit_p1": 70.0,
        "atr_len_p1": 10,
        "factor_p1": 2.0,
        "body_atr_coef_p1": 2.0,
        "ema_len_p1": 20,
        "atr_len_p2": 14,
        "highest_len_p2": 10,
        "correction_p2": 37.0,
        "ema_len_p2": 5,
        "atr_len_p3": 14,
        "ema_len_p3": 55,
        "close_under_ema_p3": 3
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_atr_p2': [i / 10 for i in range(1, 30)],
        'stop_atr_p3': [i / 10 for i in range(1, 30)],
        'take_atr_p3': [i / 10 for i in range(10, 60)],
        'fast_len_p1': [i for i in range(6, 20)],
        'slow_len_p1': [i for i in range(20, 50)],
        'sig_len_p1': [i for i in range(8, 25)],
        'k_len_p1': [i for i in range(10, 20)],
        'd_len_p1': [i for i in range(2, 6)],
        'kd_limit_p1': [float(i) for i in range(40, 100, 5)],
        'atr_len_p1': [i for i in range(5, 20)],
        'factor_p1': [i / 10 for i in range(10, 40)],
        'body_atr_coef_p1': [i / 10 for i in range(5, 30)],
        'ema_len_p1': [i for i in range(5, 30)],
        'atr_len_p2': [i for i in range(5, 30)],
        'highest_len_p2': [i for i in range(5, 20)],
        'correction_p2': [float(i) for i in range(20, 50)],
        'ema_len_p2': [i for i in range(2, 15)],
        'atr_len_p3': [i for i in range(5, 25)],
        'ema_len_p3': [i for i in range(40, 80)],
        'close_under_ema_p3': [i for i in range(1, 5)]
    }

    # For frontend
    indicator_options = {
        'SL': {'color': '#FF0000'},
        'TP': {'color': '#008000'}
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
        self.open = market_data['klines'][:, 1]
        self.high = market_data['klines'][:, 2]
        self.low = market_data['klines'][:, 3]
        self.close = market_data['klines'][:, 4]
        self.p_precision = market_data['p_precision']
        self.q_precision = market_data['q_precision']

        self.equity = self.params['initial_capital']
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.full(self.time.shape[0], np.nan)
        self.liquidation_price = np.nan
        self.deal_p1 = False
        self.deal_p2 = False
        self.deal_p3 = False
        self.filter1_p1 = False
        self.filter2_p1 = False
        self.filter3_p1 = False
        self.short_allowed_p3 = False
        self.close_under_ema_counter_p3 = 0

        self.macd_p1 = (
            ta.ema(
                source=self.close,
                length=self.params['fast_len_p1']
            ) -
            ta.ema(
                source=self.close,
                length=self.params['slow_len_p1']
            )
        )
        self.signal_p1 = ta.ema(
            source=self.macd_p1,
            length=self.params['sig_len_p1']
        )
        self.k_p1 = ta.stoch(
            source=self.close,
            high=self.high,
            low=self.low,
            length=self.params['k_len_p1']
        )
        self.d_p1 = ta.sma(source=self.k_p1, length=self.params['d_len_p1'])
        supertrend = ta.supertrend(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['factor_p1'],
            atr_length=self.params['atr_len_p1']
        )
        self.direction_p1 = supertrend[1]
        self.atr_p1 = ta.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p1']
        )
        self.ema_p1 = ta.ema(
            source=ta.highest(
                source=self.close,
                length=self.params['ema_len_p1']
            ),
            length=self.params['ema_len_p1']
        )
        self.cross_up1_p1 = ta.crossover(
            source1=self.macd_p1,
            source2=self.signal_p1
        )
        self.cross_down_p1 = ta.crossunder(
            source1=self.macd_p1,
            source2=self.signal_p1
        )
        self.cross_up2_p1 = ta.crossover(
            source1=self.close,
            source2=self.ema_p1
        )
        self.lower_band_p2 = (
            ta.highest(
                source=self.high,
                length=self.params['highest_len_p2']
            ) * (self.params['correction_p2'] - 100) / -100
        )
        self.signal_p2 = ta.ema(
            source=self.macd_p1,
            length=self.params['ema_len_p2']
        )
        self.cross_p2 = ta.cross(source1=self.signal_p2, source2=self.macd_p1)
        self.atr_p2 = ta.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p2']
        )
        self.ema_p3 = ta.ema(
            source=ta.ema(
                source=ta.ema(
                    source=self.close,
                    length=self.params['ema_len_p3']
                ),
                length=self.params['ema_len_p3']
            ),
            length=self.params['ema_len_p3']
        )
        self.atr_p3 = ta.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p3']
        )

        self.alert_entry_long = False
        self.alert_exit_long = False
        self.alert_entry_short = False
        self.alert_exit_short = False
        self.alert_cancel = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.take_price,
            self.stop_price,
            self.alert_entry_long,
            self.alert_exit_long,
            self.alert_entry_short,
            self.alert_exit_short,
            self.alert_cancel
        ) = self._calculate(
                self.params['direction'],
                self.params['initial_capital'],
                self.params['commission'],
                self.params['order_size_type'],
                self.params['order_size'],
                self.params['leverage'],
                self.params['stop_atr_p2'],
                self.params['stop_atr_p3'],
                self.params['take_atr_p3'],
                self.params['kd_limit_p1'],
                self.params['body_atr_coef_p1'],
                self.params['close_under_ema_p3'],
                self.p_precision,
                self.q_precision,
                self.time,
                self.open,
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
                self.take_price,
                self.stop_price,
                self.liquidation_price,
                self.position_size,
                self.deal_p1,
                self.deal_p2,
                self.deal_p3,
                self.filter1_p1,
                self.filter2_p1,
                self.filter3_p1,
                self.short_allowed_p3,
                self.close_under_ema_counter_p3,
                self.macd_p1,
                self.signal_p1,
                self.k_p1,
                self.d_p1,
                self.direction_p1,
                self.atr_p1,
                self.cross_up1_p1,
                self.cross_down_p1,
                self.cross_up2_p1,
                self.lower_band_p2,
                self.cross_p2,
                self.atr_p2,
                self.ema_p3,
                self.atr_p3,
                self.alert_entry_long,
                self.alert_exit_long,
                self.alert_entry_short,
                self.alert_exit_short,
                self.alert_cancel
        )

        self.indicators = {
            'SL': {
                'options': self.indicator_options['SL'],
                'values': self.stop_price
            },
            'TP': {
                'options': self.indicator_options['TP'],
                'values': self.take_price
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
        stop_atr_p2: float,
        stop_atr_p3: float,
        take_atr_p3: float,
        kd_limit_p1: float,
        body_atr_coef_p1: float,
        close_under_ema_p3,
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
        deal_p1: bool,
        deal_p2: bool,
        deal_p3: bool,
        filter1_p1: bool,
        filter2_p1: bool,
        filter3_p1: bool,
        short_allowed_p3: bool,
        close_under_ema_counter_p3: int,
        macd_p1: np.ndarray,
        signal_p1: np.ndarray,
        k_p1: np.ndarray,
        d_p1: np.ndarray,
        direction_p1: np.ndarray,
        atr_p1: np.ndarray,
        cross_up1_p1: np.ndarray,
        cross_down_p1: np.ndarray,
        cross_up2_p1: np.ndarray,
        lower_band_p2: np.ndarray,
        cross_p2: np.ndarray,
        atr_p2: np.ndarray,
        ema_p3: np.ndarray,
        atr_p3: np.ndarray,
        alert_entry_long: bool,
        alert_exit_long: bool,
        alert_entry_short: bool,
        alert_exit_short: bool,
        alert_cancel: bool
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

        for i in range(2, time.shape[0]):
            alert_entry_long = False
            alert_exit_long = False
            alert_entry_short = False
            alert_exit_short = False
            alert_cancel = False

            if i > 0:
                stop_price[i] = stop_price[i - 1]
                take_price[i] = take_price[i - 1]

            # Pattern #3 — indicators
            if close[i] > ema_p3[i]:
                short_allowed_p3 = True

            if close[i] < ema_p3[i]:
                close_under_ema_counter_p3 += 1
            else:
                close_under_ema_counter_p3 = 0

            # Pattern #1 — filters
            filter1_p1_off = (
                filter1_p1 and (
                    direction_p1[i] < 0 and (
                        direction_p1[i - 1] > 0 and (
                            k_p1[i] < kd_limit_p1 or 
                            d_p1[i] < kd_limit_p1
                        )
                    ) or 
                    macd_p1[i] < signal_p1[i]
                )
            )
            filter1_p1_on = direction_p1[i] > 0 and close[i] < ema_p3[i]

            if filter1_p1_off:
                filter1_p1 = False
            elif filter1_p1_on:
                filter1_p1 = True

            filter2_p1_off = filter2_p1 and cross_down_p1[i]
            filter2_p1_on = (
                close[i] < ema_p3[i] and
                close[i] > open[i] and
                (close[i] - open[i]) / atr_p1[i - 1] > body_atr_coef_p1
            )

            if filter2_p1_off:
                filter2_p1 = False
            elif filter2_p1_on:
                filter2_p1 = True

            filter3_p1_off = filter3_p1
            filter3_p1_on = (
                macd_p1[i - 1] < signal_p1[i - 1] and
                macd_p1[i - 2] > signal_p1[i - 2]
            )

            if filter3_p1_off:
                filter3_p1 = False
            elif filter3_p1_on:
                filter3_p1 = True

            # Check of liquidation
            if (deal_p1 or deal_p1) and low[i] <= liquidation_price:
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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
                deal_p1 = False
                deal_p2 = False

            if deal_p3 and high[i] >= liquidation_price:
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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
                deal_p3 = False
                alert_cancel = True

            # Pattern #1
            exit_long_p1 = (
                cross_down_p1[i] and
                deal_p1
            )
            entry_long1_p1 = (
                macd_p1[i] > signal_p1[i] and
                low[i] > lower_band_p2[i] and
                not filter1_p1
            )
            entry_long2_p1 = (
                macd_p1[i] > signal_p1[i] and
                low[i] > lower_band_p2[i] and
                cross_up2_p1[i] and
                filter1_p1
            )
            entry_long_p1 = (
                (entry_long1_p1 or entry_long2_p1) and
                not filter2_p1 and
                not filter3_p1 and
                not deal_p1 and
                not deal_p2 and
                (direction == 0 or direction == 1)
            )

            if exit_long_p1:
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    13,
                    entry_date,
                    time[i],
                    entry_price,
                    close[i],
                    position_size,
                    initial_capital
                )

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                deal_p1 = False
                alert_exit_long = True
            elif entry_long_p1:
                deal_p1 = True

                if deal_p3:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        14,
                        entry_date,
                        time[i],
                        entry_price,
                        close[i],
                        position_size,
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    liquidation_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    position_size = np.nan
                    deal_p3 = False
                    short_allowed_p3 = False
                    alert_exit_short = True
                    alert_cancel = True

                if deal_p2:
                    deal_p2 = False
                    stop_price[i] = np.nan
                else:
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
                    position_size = adjust(
                        position_size, q_precision
                    )
                    open_deals_log = np.array(
                        [
                            deal_type, entry_signal, entry_date,
                            entry_price, position_size
                        ]
                    )
                    alert_entry_long = True

            # Pattern #2
            exit_long_p2 = (
                (cross_p2[i] or close[i] < stop_price[i]) and
                deal_p2
            )
            entry_long_p2 = (
                low[i] <= lower_band_p2[i] and
                not deal_p2 and
                (direction == 0 or direction == 1)
            )

            if exit_long_p2:
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    13,
                    entry_date,
                    time[i],
                    entry_price,
                    close[i],
                    position_size,
                    initial_capital
                )

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                deal_p2 = False
                alert_exit_long = True
            elif entry_long_p2:
                deal_p2 = True

                if deal_p1:
                    deal_p1 = False

                if deal_p3:
                    completed_deals_log, equity = update_log(
                        completed_deals_log,
                        equity,
                        commission,
                        deal_type,
                        entry_signal,
                        14,
                        entry_date,
                        time[i],
                        entry_price,
                        close[i],
                        position_size,
                        initial_capital
                    )

                    open_deals_log = np.full(5, np.nan)
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    liquidation_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    position_size = np.nan
                    deal_p3 = False
                    short_allowed_p3 = False
                    alert_exit_short = True
                    alert_cancel = True

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
                stop_price[i] = adjust(
                    close[i] - atr_p2[i] * stop_atr_p2, p_precision
                )
                liquidation_price = adjust(
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                position_size = adjust(
                    position_size, q_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_entry_long = True

            # Pattern #3
            if deal_p3 and low[i] <= take_price[i]:
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    12,
                    entry_date,
                    time[i],
                    entry_price,
                    take_price[i],
                    position_size,
                    initial_capital
                )

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                position_size = np.nan
                deal_p3 = False
                short_allowed_p3 = False


            exit_short_p3 = (
                (
                    (close[i] > stop_price[i] or cross_up1_p1[i]) and deal_p3
                ) or 
                (low[i] < lower_band_p2[i] and deal_p3)
            )
            entry_short_p3 = (
                short_allowed_p3 and
                close_under_ema_counter_p3 >= close_under_ema_p3 and
                macd_p1[i] < signal_p1[i] and
                not deal_p1 and
                not deal_p2 and
                not deal_p3 and
                (direction == 0 or direction == 2)
            )

            if exit_short_p3:
                completed_deals_log, equity = update_log(
                    completed_deals_log,
                    equity,
                    commission,
                    deal_type,
                    entry_signal,
                    14,
                    entry_date,
                    time[i],
                    entry_price,
                    close[i],
                    position_size,
                    initial_capital
                )

                open_deals_log = np.full(5, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                liquidation_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
                deal_p3 = False
                short_allowed_p3 = False
                alert_exit_short = True
                alert_cancel = True
            elif entry_short_p3:
                deal_p3 = True
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
                stop_price[i] = adjust(
                    close[i] + atr_p3[i] * stop_atr_p3, p_precision
                )
                take_price[i] = adjust(
                    close[i] - atr_p3[i] * take_atr_p3, p_precision
                )
                liquidation_price = adjust(
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                position_size = adjust(
                    position_size, q_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_entry_short = True

        return (
            completed_deals_log,
            open_deals_log,
            take_price,
            stop_price,
            alert_entry_long,
            alert_exit_long,
            alert_entry_short,
            alert_exit_short,
            alert_cancel
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

        if self.alert_exit_long:
            self.client.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_exit_short:
            self.client.market_close_short(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_entry_long:
            self.client.market_open_long(
                symbol=self.symbol,
                size=f'{self.params['order_size']}%',
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            if not np.isnan(self.stop_price[-1]):
                order_id = self.client.market_stop_close_long(
                    symbol=self.symbol, 
                    size='100%', 
                    price=self.stop_price[-1], 
                    hedge=False
                )

                if order_id:
                    self.order_ids['stop_ids'].append(order_id)

        if self.alert_entry_short:
            self.client.market_open_short(
                symbol=self.symbol,
                size=f'{self.params['order_size']}%',
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