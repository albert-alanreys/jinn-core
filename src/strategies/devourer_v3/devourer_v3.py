import numpy as np
import numba as nb

from ..strategy import Strategy
from ... import ta


class DevourerV3(Strategy):
    # Strategy parameters
    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    margin_type = 0
    # direction: 0 - 'all', 1 — 'longs', 2 — 'shorts'
    direction = 0
    initial_capital = 10000.0
    commission = 0.05
    order_size_type = 0
    order_size = 100.0
    leverage = 1
    stop_atr_p2 = 0.5
    stop_atr_p3 = 1.0
    take_atr_p3 = 3.0
    fast_len_p1 = 12
    slow_len_p1 = 26
    sig_len_p1 = 14
    k_len_p1 = 14
    d_len_p1 = 3
    kd_limit_p1 = 70.0
    atr_len_p1 = 10
    factor_p1 = 2.0
    body_atr_coef_p1 = 2.0
    ema_len_p1 = 20
    atr_len_p2 = 14
    highest_len_p2 = 10
    correction_p2 = 37.0
    ema_len_p2 = 5
    atr_len_p3 = 14
    ema_len_p3 = 55
    close_under_ema_p3 = 3

    # Parameters to be optimized and their possible values
    opt_parameters = {
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
        'Stop-loss': {'color': '#FF0000'},
        'Take-profit': {'color': '#008000'}
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

    def __init__(
        self,
        opt_parameters: list | None = None,
        all_parameters: list | None = None
    ) -> None:
        for key, value in DevourerV3.__dict__.items():
            if (not key.startswith('__') and
                    key not in DevourerV3.class_attributes):
                self.__dict__[key] = value

        if opt_parameters is not None:
            self.stop_atr_p2 = opt_parameters[0]
            self.stop_atr_p3 = opt_parameters[1]
            self.take_atr_p3 = opt_parameters[2]
            self.fast_len_p1 = opt_parameters[3]
            self.slow_len_p1 = opt_parameters[4]
            self.sig_len_p1 = opt_parameters[5]
            self.k_len_p1 = opt_parameters[6]
            self.d_len_p1 = opt_parameters[7]
            self.kd_limit_p1 = opt_parameters[8]
            self.atr_len_p1 = opt_parameters[9]
            self.factor_p1 = opt_parameters[10]
            self.body_atr_coef_p1 = opt_parameters[11]
            self.ema_len_p1 = opt_parameters[12]
            self.atr_len_p2 = opt_parameters[13]
            self.highest_len_p2 = opt_parameters[14]
            self.correction_p2 = opt_parameters[15]
            self.ema_len_p2 = opt_parameters[16]
            self.atr_len_p3 = opt_parameters[17]
            self.ema_len_p3 = opt_parameters[18]
            self.close_under_ema_p3 = opt_parameters[19]

        if all_parameters is not None:
            self.margin_type = all_parameters[0]
            self.direction = all_parameters[1]
            self.initial_capital = all_parameters[2]
            self.commission = all_parameters[3]
            self.order_size_type = all_parameters[4]
            self.order_size = all_parameters[5]
            self.leverage = all_parameters[6]
            self.stop_atr_p2 = all_parameters[7]
            self.stop_atr_p3 = all_parameters[8]
            self.take_atr_p3 = all_parameters[9]
            self.fast_len_p1 = all_parameters[10]
            self.slow_len_p1 = all_parameters[11]
            self.sig_len_p1 = all_parameters[12]
            self.k_len_p1 = all_parameters[13]
            self.d_len_p1 = all_parameters[14]
            self.kd_limit_p1 = all_parameters[15]
            self.atr_len_p1 = all_parameters[16]
            self.factor_p1 = all_parameters[17]
            self.body_atr_coef_p1 = all_parameters[18]
            self.ema_len_p1 = all_parameters[19]
            self.atr_len_p2 = all_parameters[20]
            self.highest_len_p2 = all_parameters[21]
            self.correction_p2 = all_parameters[22]
            self.ema_len_p2 = all_parameters[23]
            self.atr_len_p3 = all_parameters[24]
            self.ema_len_p3 = all_parameters[25]
            self.close_under_ema_p3 = all_parameters[26]

    def start(self, client) -> None:
        super().__init__()

        self.price_precision = client.price_precision
        self.qty_precision = client.qty_precision
        self.time = client.price_data[:, 0]
        self.open = client.price_data[:, 1]
        self.high = client.price_data[:, 2]
        self.low = client.price_data[:, 3]
        self.close = client.price_data[:, 4]

        self.equity = self.initial_capital
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
            ta.ema(self.close, self.fast_len_p1) -
            ta.ema(self.close, self.slow_len_p1)
        )
        self.signal_p1 = ta.ema(self.macd_p1, self.sig_len_p1)
        self.k_p1 = ta.stoch(self.close, self.high, self.low, self.k_len_p1)
        self.d_p1 = ta.sma(self.k_p1, self.d_len_p1)
        self.direction_p1 = ta.supertrend(
            self.high, self.low, self.close, self.factor_p1, self.atr_len_p1
        )[1]
        self.atr_p1 = ta.atr(self.high, self.low, self.close, self.atr_len_p1)
        self.ema_p1 = ta.ema(
            ta.highest(self.close, self.ema_len_p1), self.ema_len_p1
        )
        self.cross_up1_p1 = ta.crossover(self.macd_p1, self.signal_p1)
        self.cross_down_p1 = ta.crossunder(self.macd_p1, self.signal_p1)
        self.cross_up2_p1 = ta.crossover(self.close, self.ema_p1)
        self.lower_band_p2 = (
            ta.highest(self.high, self.highest_len_p2) *
            (self.correction_p2 - 100) / -100
        )
        self.signal_p2 = ta.ema(self.macd_p1, self.ema_len_p2)
        self.cross_p2 = ta.cross(self.signal_p2, self.macd_p1)
        self.atr_p2 = ta.atr(self.high, self.low, self.close, self.atr_len_p2)
        self.ema_p3 = ta.ema(
            ta.ema(ta.ema(self.close, self.ema_len_p3), self.ema_len_p3),
            self.ema_len_p3
        )
        self.atr_p3 = ta.atr(self.high, self.low, self.close, self.atr_len_p3)

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
        ) = self.calculate(
                self.direction,
                self.initial_capital,
                self.commission,
                self.order_size_type,
                self.order_size,
                self.leverage,
                self.stop_atr_p2,
                self.stop_atr_p3,
                self.take_atr_p3,
                self.kd_limit_p1,
                self.body_atr_coef_p1,
                self.close_under_ema_p3,
                self.price_precision,
                self.qty_precision,
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
            'Stop-loss': {
                'options': self.indicator_options['Stop-loss'],
                'values': self.stop_price
            },
            'Take-profit': {
                'options': self.indicator_options['Take-profit'],
                'values': self.take_price
            }
        }

    @staticmethod
    @nb.jit(
        nb.types.Tuple((
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean 
        ))(
            nb.int8,
            nb.float64,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.int16,
            nb.float64,
            nb.float64,
            nb.float64[:],
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
            nb.float64[:],
            nb.float64[:],
            nb.float64,
            nb.float64,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.int16,
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.boolean[:],
            nb.boolean[:],
            nb.boolean[:],
            nb.float64[:],
            nb.boolean[:],
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
        price_precision: float,
        qty_precision: float,
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
        def round_to_minqty_or_mintick(number: float, precision: float) -> float:
            return round(round(number / precision) * precision, 8)

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
                    liquidation_price = round_to_minqty_or_mintick(
                        entry_price * (1 - (1 / leverage)), price_precision
                    )
                    position_size = round_to_minqty_or_mintick(
                        position_size, qty_precision
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
                stop_price[i] = round_to_minqty_or_mintick(
                    close[i] - atr_p2[i] * stop_atr_p2, price_precision
                )
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 - (1 / leverage)), price_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, qty_precision
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
                stop_price[i] = round_to_minqty_or_mintick(
                    close[i] + atr_p3[i] * stop_atr_p3, price_precision
                )
                take_price[i] = round_to_minqty_or_mintick(
                    close[i] - atr_p3[i] * take_atr_p3, price_precision
                )
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 + (1 / leverage)), price_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, qty_precision
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
        if self.alert_cancel:
            self.client.futures_cancel_all_orders(
                symbol=self.client.symbol
            )

        self.client.check_stop_status(self.client.symbol)
        self.client.check_limit_status(self.client.symbol)

        if self.alert_exit_long:
            self.client.futures_market_close_sell(
                symbol=self.client.symbol,
                size='100%',
                hedge='false'
            )

        if self.alert_exit_short:
            self.client.futures_market_close_buy(
                symbol=self.client.symbol,
                size='100%',
                hedge='false'
            )

        if self.alert_entry_long:
            self.client.futures_market_open_buy(
                symbol=self.client.symbol,
                size=f'{self.order_size}%',
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=str(self.leverage),
                hedge='false'
            )

            if not np.isnan(self.stop_price[-1]):
                self.client.futures_market_stop_sell(
                    symbol=self.client.symbol, 
                    size='100%', 
                    price=self.stop_price[-1], 
                    hedge='false'
                )

        if self.alert_entry_short:
            self.client.futures_market_open_sell(
                symbol=self.client.symbol,
                size=f'{self.order_size}%',
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
                size='100%',
                price=self.take_price[-1],
                hedge='false'
            )