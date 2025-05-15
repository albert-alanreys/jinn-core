import numpy as np
import numba as nb

import src.core.ta as ta


class NuggetV4():
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
    order_size = 100.0
    leverage = 1
    stop_type = 1
    stop = 1.0
    trail_stop = 4
    trail_percent = 0.0
    take_volume_1 = [10.0, 10.0, 10.0, 10.0, 60.0]
    take_volume_2 = [10.0, 5.0, 5.0, 5.0, 5.0, 5.0, 10.0, 15.0, 10.0, 30.0]
    st_atr_period = 7
    st_factor = 10.5
    st_upper_band = 4.8
    st_lower_band = 2.2
    rsi_length = 7
    rsi_long_upper_bound = 47.0
    rsi_long_lower_bound = 1.0
    rsi_short_upper_bound = 100.0
    rsi_short_lower_bound = 58.0
    bb_filter = False
    ma_length = 6
    bb_mult = 2.5
    bb_long_bound = 44.0
    bb_short_bound = 55.0
    pivot_bars = 2
    look_back = 35
    channel_range = 7.0

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
        'rsi_long_upper_bound': [float(i) for i in range(29, 51)],
        'rsi_long_lower_bound': [float(i) for i in range(1, 29)],
        'rsi_short_upper_bound': [float(i) for i in range(68, 101)],
        'rsi_short_lower_bound': [float(i) for i in range(50, 68)],
        'bb_filter': [True, False],
        'ma_length': [i for i in range(3, 26)],
        'bb_mult': [i / 10 for i in range(10, 31)],
        'bb_long_bound': [float(i) for i in range(20, 51)],
        'bb_short_bound': [float(i) for i in range(50, 81)],
        'pivot_bars': [i for i in range(1, 21)],
        'look_back': [i for i in range(10, 101, 5)],
        'channel_range': [float(i) for i in range(3, 21)]
    }

    # For frontend
    line_options = {
        'SL': {'color': '#FF0000'},
        'TP #1': {'color': '#008000'},
        'TP #2': {'color': '#008000'},
        'TP #3': {'color': '#008000'},
        'TP #4': {'color': '#008000'},
        'TP #5': {'color': '#008000'},
        'TP #6': {'color': '#008000'},
        'TP #7': {'color': '#008000'},
        'TP #8': {'color': '#008000'},
        'TP #9': {'color': '#008000'},
        'TP #10': {'color': '#008000'}
    }

    # Class attributes
    class_attributes = (
        'opt_params',
        'line_options',
        'class_attributes',
        'start',
        'calculate',
        'trade'
    )

    def __init__(
        self,
        opt_params: list | None = None,
        all_params: list | None = None
    ) -> None:
        for key, value in NuggetV4.__dict__.items():
            if (not key.startswith('__') and
                    key not in NuggetV4.class_attributes):
                self.__dict__[key] = value

        if opt_params is not None:
            self.stop_type = opt_params[0]
            self.stop = opt_params[1]
            self.trail_stop = opt_params[2]
            self.trail_percent = opt_params[3]
            self.take_volume_1 = opt_params[4]
            self.take_volume_2 = opt_params[5]
            self.st_atr_period = opt_params[6]
            self.st_factor = opt_params[7]
            self.st_upper_band = opt_params[8]
            self.st_lower_band = opt_params[9]
            self.rsi_length = opt_params[10]
            self.rsi_long_upper_bound = opt_params[11]
            self.rsi_long_lower_bound = opt_params[12]
            self.rsi_short_upper_bound = opt_params[13]
            self.rsi_short_lower_bound = opt_params[14]
            self.bb_filter = opt_params[15]
            self.ma_length = opt_params[16]
            self.bb_mult = opt_params[17]
            self.bb_long_bound = opt_params[18]
            self.bb_short_bound = opt_params[19]
            self.pivot_bars = opt_params[20]
            self.look_back = opt_params[21]
            self.channel_range = opt_params[22]

        if all_params is not None:
            self.margin_type = all_params[0]
            self.direction = all_params[1]
            self.initial_capital = all_params[2]
            self.min_capital = all_params[3]
            self.commission = all_params[4]
            self.order_size_type = all_params[5]
            self.order_size = all_params[6]
            self.leverage = all_params[7]
            self.stop_type = all_params[8]
            self.stop = all_params[9]
            self.trail_stop = all_params[10]
            self.trail_percent = all_params[11]
            self.take_volume_1 = all_params[12]
            self.take_volume_2 = all_params[13]
            self.st_atr_period = all_params[14]
            self.st_factor = all_params[15]
            self.st_upper_band = all_params[16]
            self.st_lower_band = all_params[17]
            self.rsi_length = all_params[18]
            self.rsi_long_upper_bound = all_params[19]
            self.rsi_long_lower_bound = all_params[20]
            self.rsi_short_upper_bound = all_params[21]
            self.rsi_short_lower_bound = all_params[22]
            self.bb_filter = all_params[23]
            self.ma_length = all_params[24]
            self.bb_mult = all_params[25]
            self.bb_long_bound = all_params[26]
            self.bb_short_bound = all_params[27]
            self.pivot_bars = all_params[28]
            self.look_back = all_params[29]
            self.channel_range = all_params[30]

    def start(self, exchange_data: dict) -> None:
        self.open_deals_log = np.full(5, np.nan)
        self.completed_deals_log = np.array([])
        self.position_size = np.nan
        self.entry_signal = np.nan
        self.entry_price = np.nan
        self.entry_date = np.nan
        self.deal_type = np.nan

        self.client = exchange_data.get('client', None)
        self.time = exchange_data['klines'][:, 0]
        self.high = exchange_data['klines'][:, 2]
        self.low = exchange_data['klines'][:, 3]
        self.close = exchange_data['klines'][:, 4]
        self.p_precision = exchange_data['p_precision']
        self.q_precision = exchange_data['q_precision']

        self.equity = self.initial_capital
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
        self.ds = ta.ds(self.high, self.low, self.close,
                        self.st_factor, self.st_atr_period)
        self.change_upper_band = ta.change(self.ds[0], 1)
        self.change_lower_band = ta.change(self.ds[1], 1)
        self.rsi = ta.rsi(self.close, self.rsi_length)

        if self.bb_filter:
            self.bb_rsi = ta.bb(
                self.rsi, self.ma_length, self.bb_mult)
        else:
            self.bb_rsi = np.full(self.time.shape[0], np.nan)

        self.pivot_LH = ta.pivothigh(
            self.high, self.pivot_bars, self.pivot_bars)
        self.pivot_HL = ta.pivotlow(
            self.low, self.pivot_bars, self.pivot_bars)
        self.fibo_values = np.array(
            [
                0.0, 0.236, 0.382, 0.5, 0.618, 0.8, 1.0,
                1.618, 2.0, 2.618, 3.0, 3.618, 4.0
            ]
        )
        self.fibo_levels = np.full(13, np.nan)
        self.alert_long_1 = False
        self.alert_long_2 = False
        self.alert_short_1 = False
        self.alert_short_2 = False
        self.alert_long_new_stop = False
        self.alert_short_new_stop = False
        self.alert_cancel = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.stop_price,
            self.take_price,
            self.alert_long_1,
            self.alert_long_2,
            self.alert_short_1,
            self.alert_short_2,
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
                self.stop_type,
                self.stop,
                self.trail_stop,
                self.trail_percent,
                self.take_volume_1,
                self.take_volume_2,
                self.st_upper_band,
                self.st_lower_band,
                self.rsi_long_upper_bound,
                self.rsi_long_lower_bound,
                self.rsi_short_upper_bound,
                self.rsi_short_lower_bound,
                self.bb_filter,
                self.bb_long_bound,
                self.bb_short_bound,
                self.pivot_bars,
                self.look_back,
                self.channel_range,
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
                self.position_size,
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
                self.ds[0],
                self.ds[1],
                self.change_upper_band,
                self.change_lower_band,
                self.rsi,
                self.bb_rsi[1] if self.bb_filter else self.bb_rsi,
                self.bb_rsi[2] if self.bb_filter else self.bb_rsi,
                self.pivot_LH,
                self.pivot_HL,
                self.fibo_values,
                self.fibo_levels,
                self.alert_long_1,
                self.alert_long_2,
                self.alert_short_1,
                self.alert_short_2,
                self.alert_long_new_stop,
                self.alert_short_new_stop,
                self.alert_cancel
        )

        self.lines = {
            'SL': {
                'options': self.line_options['SL'],
                'values': self.stop_price
            },
            'TP #1': {
                'options': self.line_options['TP #1'],
                'values': self.take_price[0]
            },
            'TP #2': {
                'options': self.line_options['TP #2'],
                'values': self.take_price[1]
            },
            'TP #3': {
                'options': self.line_options['TP #3'],
                'values': self.take_price[2]
            },
            'TP #4': {
                'options': self.line_options['TP #4'],
                'values': self.take_price[3]
            },
            'TP #5': {
                'options': self.line_options['TP #5'],
                'values': self.take_price[4]
            },
            'TP #6': {
                'options': self.line_options['TP #6'],
                'values': self.take_price[5]
            },
            'TP #7': {
                'options': self.line_options['TP #7'],
                'values': self.take_price[6]
            },
            'TP #8': {
                'options': self.line_options['TP #8'],
                'values': self.take_price[7]
            },
            'TP #9': {
                'options': self.line_options['TP #9'],
                'values': self.take_price[8]
            },
            'TP #10': {
                'options': self.line_options['TP #10'],
                'values': self.take_price[9]
            }
        }

    @staticmethod
    @nb.jit(
        nb.types.Tuple((
            nb.float64[:],
            nb.float64[:],
            nb.float64[:],
            nb.float64[:, :],
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean,
            nb.boolean
        ))(
            nb.int8,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.int8,
            nb.int8,
            nb.float64,
            nb.int8,
            nb.float64,
            nb.types.List(nb.float64, reflected=True),
            nb.types.List(nb.float64, reflected=True),
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.float64,
            nb.boolean,
            nb.float64,
            nb.float64,
            nb.int16,
            nb.int16,
            nb.float64,
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
            nb.float64,
            nb.float64[:],
            nb.float64[:, :],
            nb.float64[:],
            nb.float64[:],
            nb.int8,
            nb.float64,
            nb.float64[:],
            nb.float64[:],
            nb.float64,
            nb.float64[:],
            nb.float64[:],
            nb.float64,
            nb.float64,
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
            nb.float64[:],
            nb.float64[:],
            nb.boolean,
            nb.boolean,
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
        min_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop_type: int,
        stop: float,
        trail_stop: int,
        trail_percent: float,
        take_volume_1: list,
        take_volume_2: list,
        st_upper_band: float,
        st_lower_band: float,
        rsi_long_upper_bound: float,
        rsi_long_lower_bound: float,
        rsi_short_upper_bound: float,
        rsi_short_lower_bound: float,
        bb_filter: bool,
        bb_long_bound: float,
        bb_short_bound: float,
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
        deal_type: float,
        entry_signal: float,
        entry_date: float,
        entry_price: float,
        liquidation_price: float,
        position_size: float,
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
        ds_upper_band: np.ndarray,
        ds_lower_band: np.ndarray,
        change_upper_band: np.ndarray,
        change_lower_band: np.ndarray,
        rsi: np.ndarray,
        bb_rsi_upper: np.ndarray,
        bb_rsi_lower: np.ndarray,
        pivot_LH: np.ndarray,
        pivot_HL: np.ndarray,
        fibo_values: np.ndarray,
        fibo_levels: np.ndarray,
        alert_long_1: bool,
        alert_long_2: bool,
        alert_short_1: bool,
        alert_short_2: bool,
        alert_long_new_stop: bool,
        alert_short_new_stop: bool,
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
        
        for i in range(time.shape[0]):
            alert_long_1 = False
            alert_long_2 = False
            alert_short_1 = False
            alert_short_2 = False
            alert_long_new_stop = False
            alert_short_new_stop = False
            alert_cancel = False

            if i > 0:
                stop_price[i] = stop_price[i - 1]
                take_price[:, i : i + 1] = take_price[:, i - 1 : i]

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
                position_size = np.nan
                stop_price[i] = np.nan
                take_price[:, i : i + 1] = np.full(10, np.nan).reshape((10, 1))
                qty_take_1 = np.full(5, np.nan)
                qty_take_2 = np.full(10, np.nan)
                stop_moved = False
                grid_type = np.nan
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
                position_size = np.nan
                stop_price[i] = np.nan
                take_price[:, i : i + 1] = np.full(10, np.nan).reshape((10, 1))
                qty_take_1 = np.full(5, np.nan)
                qty_take_2 = np.full(10, np.nan)
                stop_moved = False
                grid_type = np.nan
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
                    position_size = np.nan
                    stop_price[i] = np.nan
                    take_price[:, i : i + 1] = np.full(10, np.nan).reshape((10, 1))
                    qty_take_1 = np.full(5, np.nan)
                    qty_take_2 = np.full(10, np.nan)
                    stop_moved = False
                    grid_type = np.nan
                    alert_cancel = True

                if (stop_type == 1 and
                        change_lower_band[i] and
                        ((ds_lower_band[i] * (100 - stop)
                        / 100) > stop_price[i])):
                    stop_price[i] = round_to_minqty_or_mintick(
                        ds_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                    alert_long_new_stop = True
                elif (stop_type == 2 or stop_type == 3) and not stop_moved:
                    take = None

                    if grid_type == 0:
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
                    elif grid_type == 1:
                        if (trail_stop == 9 and
                                high[i] >= take_price[8][i]):
                            take = take_price[8][i]
                        elif (trail_stop == 8 and
                                high[i] >= take_price[7][i]):
                            take = take_price[7][i]
                        elif (trail_stop == 7 and
                                high[i] >= take_price[6][i]):
                            take = take_price[6][i]
                        elif (trail_stop == 6 and
                                high[i] >= take_price[5][i]):
                            take = take_price[5][i]
                        elif (trail_stop == 5 and
                                high[i] >= take_price[4][i]):
                            take = take_price[4][i]
                        elif (trail_stop == 4 and
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
                        stop_price[i] = round_to_minqty_or_mintick(
                            (take - entry_price) * (trail_percent / 100)
                                + entry_price,
                            p_precision
                        )
                        alert_long_new_stop = True

                if grid_type == 0:
                    if (not np.isnan(take_price[0][i]) and 
                            high[i] >= take_price[0][i]):
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
                            qty_take_1[0],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_1[0], 8)
                        open_deals_log[4] = position_size
                        take_price[0][i] = np.nan
                        qty_take_1[0] = np.nan

                    if (not np.isnan(take_price[1][i]) and 
                            high[i] >= take_price[1][i]):
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
                            qty_take_1[1],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_1[1], 8)
                        open_deals_log[4] = position_size
                        take_price[1][i] = np.nan
                        qty_take_1[1] = np.nan

                    if (not np.isnan(take_price[2][i]) and 
                            high[i] >= take_price[2][i]):
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
                            qty_take_1[2],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_1[2], 8)
                        open_deals_log[4] = position_size
                        take_price[2][i] = np.nan
                        qty_take_1[2] = np.nan

                    if (not np.isnan(take_price[3][i]) and 
                            high[i] >= take_price[3][i]):
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
                            qty_take_1[3],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_1[3], 8)
                        open_deals_log[4] = position_size
                        take_price[3][i] = np.nan
                        qty_take_1[3] = np.nan

                    if (not np.isnan(take_price[4][i]) and 
                            high[i] >= take_price[4][i]):
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
                            round(qty_take_1[4], 8),
                            initial_capital
                        )

                        open_deals_log = np.full(5, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[4][i] = np.nan
                        qty_take_1[4] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True
                elif grid_type == 1:
                    if (not np.isnan(take_price[0][i]) and 
                            high[i] >= take_price[0][i]):
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
                            qty_take_2[0],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_2[0], 8)
                        open_deals_log[4] = position_size
                        take_price[0][i] = np.nan
                        qty_take_2[0] = np.nan

                    if (not np.isnan(take_price[1][i]) and 
                            high[i] >= take_price[1][i]):
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
                            qty_take_2[1],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_2[1], 8)
                        open_deals_log[4] = position_size
                        take_price[1][i] = np.nan
                        qty_take_2[1] = np.nan

                    if (not np.isnan(take_price[2][i]) and 
                            high[i] >= take_price[2][i]):
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
                            qty_take_2[2],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[2], 8)
                        open_deals_log[4] = position_size
                        take_price[2][i] = np.nan
                        qty_take_2[2] = np.nan

                    if (not np.isnan(take_price[3][i]) and 
                            high[i] >= take_price[3][i]):
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
                            qty_take_2[3],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[3], 8)
                        open_deals_log[4] = position_size
                        take_price[3][i] = np.nan
                        qty_take_2[3] = np.nan

                    if (not np.isnan(take_price[4][i]) and 
                            high[i] >= take_price[4][i]):
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
                            qty_take_2[4],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[4], 8)
                        open_deals_log[4] = position_size
                        take_price[4][i] = np.nan
                        qty_take_2[4] = np.nan

                    if (not np.isnan(take_price[5][i]) and 
                            high[i] >= take_price[5][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            7,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[5][i],
                            qty_take_2[5],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[5], 8)
                        open_deals_log[4] = position_size
                        take_price[5][i] = np.nan
                        qty_take_2[5] = np.nan

                    if (not np.isnan(take_price[6][i]) and 
                            high[i] >= take_price[6][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            8,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[6][i],
                            qty_take_2[6],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[6], 8)
                        open_deals_log[4] = position_size
                        take_price[6][i] = np.nan
                        qty_take_2[6] = np.nan

                    if (not np.isnan(take_price[7][i]) and 
                            high[i] >= take_price[7][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            9,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[7][i],
                            qty_take_2[7],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[7], 8)
                        open_deals_log[4] = position_size
                        take_price[7][i] = np.nan
                        qty_take_2[7] = np.nan

                    if (not np.isnan(take_price[8][i]) and 
                            high[i] >= take_price[8][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            10,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[8][i],
                            qty_take_2[8],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[8], 8)
                        open_deals_log[4] = position_size
                        take_price[8][i] = np.nan
                        qty_take_2[8] = np.nan

                    if (not np.isnan(take_price[9][i]) and 
                            high[i] >= take_price[9][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            11,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[9][i],
                            round(qty_take_2[9], 8),
                            initial_capital
                        ) 

                        open_deals_log = np.full(5, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[9][i] = np.nan
                        qty_take_2[9] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True

            pre_entry_long = (
                (close[i] / ds_lower_band[i] - 1) * 100 > st_lower_band and
                (close[i] / ds_lower_band[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_long_upper_bound and
                rsi[i] > rsi_long_lower_bound and
                np.isnan(deal_type) and
                (bb_rsi_upper[i] < bb_long_bound
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
                deal_type = 0
                entry_signal = 0
                entry_date = time[i]
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
                    initial_position = (order_size * leverage)
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                    
                position_size = round_to_minqty_or_mintick(
                    position_size, q_precision
                )
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )

                if stop_type == 1 or stop_type == 2:
                    stop_price[i] = round_to_minqty_or_mintick(
                        ds_lower_band[i] * (100 - stop) / 100,
                        p_precision
                    )
                elif stop_type == 3:
                    stop_price[i] = round_to_minqty_or_mintick(
                        fibo_levels[0] * (100 - stop) / 100, p_precision
                    )

                if last_channel_range >= channel_range:
                    grid_type = 0

                    if close[i] >= fibo_levels[0] and close[i] < fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[2], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                    elif close[i] >= fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )

                    qty_take_1[0] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[0] / 100, q_precision
                    )
                    qty_take_1[1] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[1] / 100, q_precision
                    )
                    qty_take_1[2] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[2] / 100, q_precision
                    )
                    qty_take_1[3] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[3] / 100, q_precision
                    )
                    qty_take_1[4] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[4] / 100, q_precision
                    )
                    alert_long_1 = True
                elif last_channel_range < channel_range:
                    grid_type = 1

                    if close[i] >= fibo_levels[0] and close[i] < fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[2], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[5][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )
                        take_price[6][i] = round_to_minqty_or_mintick(
                            fibo_levels[8], p_precision
                        )
                        take_price[7][i] = round_to_minqty_or_mintick(
                            fibo_levels[9], p_precision
                        )
                        take_price[8][i] = round_to_minqty_or_mintick(
                            fibo_levels[10], p_precision
                        )
                        take_price[9][i] = round_to_minqty_or_mintick(
                            fibo_levels[11], p_precision
                        )
                    elif close[i] >= fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )
                        take_price[5][i] = round_to_minqty_or_mintick(
                            fibo_levels[8], p_precision
                        )
                        take_price[6][i] = round_to_minqty_or_mintick(
                            fibo_levels[9], p_precision
                        )
                        take_price[7][i] = round_to_minqty_or_mintick(
                            fibo_levels[10], p_precision
                        )
                        take_price[8][i] = round_to_minqty_or_mintick(
                            fibo_levels[11], p_precision
                        )
                        take_price[9][i] = round_to_minqty_or_mintick(
                            fibo_levels[12], p_precision
                        )

                    qty_take_2[0] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[0] / 100, q_precision
                    )
                    qty_take_2[1] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[1] / 100, q_precision
                    )
                    qty_take_2[2] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[2] / 100, q_precision
                    )
                    qty_take_2[3] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[3] / 100, q_precision
                    )
                    qty_take_2[4] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[4] / 100, q_precision
                    )
                    qty_take_2[5] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[5] / 100, q_precision
                    )
                    qty_take_2[6] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[6] / 100, q_precision
                    )
                    qty_take_2[7] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[7] / 100, q_precision
                    )
                    qty_take_2[8] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[8] / 100, q_precision
                    )
                    qty_take_2[9] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[9] / 100, q_precision
                    )
                    alert_long_2 = True

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
                    position_size = np.nan
                    stop_price[i] = np.nan
                    take_price[:, i : i + 1] = np.full(10, np.nan).reshape((10, 1))
                    qty_take_1 = np.full(5, np.nan)
                    qty_take_2 = np.full(10, np.nan)
                    stop_moved = False
                    grid_type = np.nan
                    alert_cancel = True

                if (stop_type == 1 and
                        change_upper_band[i] and
                        ((ds_upper_band[i] * (100 + stop)
                        / 100) < stop_price[i])):
                    stop_price[i] = round_to_minqty_or_mintick(
                        (ds_upper_band[i] * (100 + stop) / 100), 
                        p_precision
                    )
                    alert_short_new_stop = True
                elif (stop_type == 2 or stop_type == 3) and not stop_moved:
                    take = None

                    if grid_type == 0:
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
                    elif grid_type == 1:
                        if (trail_stop == 9 and
                                low[i] <= take_price[8][i]):
                            take = take_price[8][i]
                        elif (trail_stop == 8 and
                                low[i] <= take_price[7][i]):
                            take = take_price[7][i]
                        elif (trail_stop == 7 and
                                low[i] <= take_price[6][i]):
                            take = take_price[6][i]
                        elif (trail_stop == 6 and
                                low[i] <= take_price[5][i]):
                            take = take_price[5][i]
                        elif (trail_stop == 5 and
                                low[i] <= take_price[4][i]):
                            take = take_price[4][i]
                        elif (trail_stop == 4 and
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
                        stop_price[i] = round_to_minqty_or_mintick(
                            (take - entry_price) * (trail_percent / 100)
                                + entry_price,
                            p_precision
                        )
                        alert_short_new_stop = True
    
                if grid_type == 0:
                    if (not np.isnan(take_price[0][i]) and 
                            low[i] <= take_price[0][i]):
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
                            qty_take_1[0],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_1[0], 8)
                        open_deals_log[4] = position_size
                        take_price[0][i] = np.nan
                        qty_take_1[0] = np.nan

                    if (not np.isnan(take_price[1][i]) and 
                            low[i] <= take_price[1][i]):
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
                            qty_take_1[1],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_1[1], 8)
                        open_deals_log[4] = position_size
                        take_price[1][i] = np.nan
                        qty_take_1[1] = np.nan

                    if (not np.isnan(take_price[2][i]) and 
                            low[i] <= take_price[2][i]):
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
                            qty_take_1[2],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_1[2], 8)
                        open_deals_log[4] = position_size
                        take_price[2][i] = np.nan
                        qty_take_1[2] = np.nan

                    if (not np.isnan(take_price[3][i]) and 
                            low[i] <= take_price[3][i]):
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
                            qty_take_1[3],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_1[3], 8)
                        open_deals_log[4] = position_size
                        take_price[3][i] = np.nan
                        qty_take_1[3] = np.nan

                    if (not np.isnan(take_price[4][i]) and 
                            low[i] <= take_price[4][i]):
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
                            round(qty_take_1[4], 8),
                            initial_capital
                        )

                        open_deals_log = np.full(5, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[4][i] = np.nan
                        qty_take_1[4] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True
                elif grid_type == 1:
                    if (not np.isnan(take_price[0][i]) and 
                            low[i] <= take_price[0][i]):
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
                            qty_take_2[0],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_2[0], 8)
                        open_deals_log[4] = position_size
                        take_price[0][i] = np.nan
                        qty_take_2[0] = np.nan

                    if (not np.isnan(take_price[1][i]) and 
                            low[i] <= take_price[1][i]):
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
                            qty_take_2[1],
                            initial_capital
                        )

                        position_size = round(position_size - qty_take_2[1], 8)
                        open_deals_log[4] = position_size
                        take_price[1][i] = np.nan
                        qty_take_2[1] = np.nan

                    if (not np.isnan(take_price[2][i]) and 
                            low[i] <= take_price[2][i]):
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
                            qty_take_2[2],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[2], 8)
                        open_deals_log[4] = position_size
                        take_price[2][i] = np.nan
                        qty_take_2[2] = np.nan

                    if (not np.isnan(take_price[3][i]) and 
                            low[i] <= take_price[3][i]):
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
                            qty_take_2[3],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[3], 8)
                        open_deals_log[4] = position_size
                        take_price[3][i] = np.nan
                        qty_take_2[3] = np.nan

                    if (not np.isnan(take_price[4][i]) and 
                            low[i] <= take_price[4][i]):
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
                            qty_take_2[4],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[4], 8)
                        open_deals_log[4] = position_size
                        take_price[4][i] = np.nan
                        qty_take_2[4] = np.nan

                    if (not np.isnan(take_price[5][i]) and 
                            low[i] <= take_price[5][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            7,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[5][i],
                            qty_take_2[5],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[5], 8)
                        open_deals_log[4] = position_size
                        take_price[5][i] = np.nan
                        qty_take_2[5] = np.nan

                    if (not np.isnan(take_price[6][i]) and 
                            low[i] <= take_price[6][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            8,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[6][i],
                            qty_take_2[6],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[6], 8)
                        open_deals_log[4] = position_size
                        take_price[6][i] = np.nan
                        qty_take_2[6] = np.nan

                    if (not np.isnan(take_price[7][i]) and 
                            low[i] <= take_price[7][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            9,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[7][i],
                            qty_take_2[7],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[7], 8)
                        open_deals_log[4] = position_size
                        take_price[7][i] = np.nan
                        qty_take_2[7] = np.nan

                    if (not np.isnan(take_price[8][i]) and 
                            low[i] <= take_price[8][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            10,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[8][i],
                            qty_take_2[8],
                            initial_capital
                        ) 

                        position_size = round(position_size - qty_take_2[8], 8)
                        open_deals_log[4] = position_size
                        take_price[8][i] = np.nan
                        qty_take_2[8] = np.nan

                    if (not np.isnan(take_price[9][i]) and 
                            low[i] <= take_price[9][i]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal_type,
                            entry_signal,
                            11,
                            entry_date,
                            time[i],
                            entry_price,
                            take_price[9][i],
                            round(qty_take_2[9], 8),
                            initial_capital
                        ) 

                        open_deals_log = np.full(5, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[9][i] = np.nan
                        qty_take_2[9] = np.nan
                        stop_price[i] = np.nan
                        stop_moved = False
                        grid_type = np.nan
                        alert_cancel = True

            pre_entry_short = (
                (ds_upper_band[i] / close[i] - 1) * 100 > st_lower_band and
                (ds_upper_band[i] / close[i] - 1) * 100 < st_upper_band and
                rsi[i] < rsi_short_upper_bound and
                rsi[i] > rsi_short_lower_bound and
                np.isnan(deal_type) and
                (bb_rsi_lower[i] > bb_short_bound
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
                deal_type = 1
                entry_signal = 1
                entry_date = time[i]
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
                    initial_position = (order_size * leverage)
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                    
                position_size = round_to_minqty_or_mintick(
                    position_size, q_precision
                )
                liquidation_price = round_to_minqty_or_mintick(
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )

                if stop_type == 1 or stop_type == 2:
                    stop_price[i] = round_to_minqty_or_mintick(
                        ds_upper_band[i] * (100 + stop) / 100,
                        p_precision
                    )
                elif stop_type == 3:
                    stop_price[i] = round_to_minqty_or_mintick(
                        fibo_levels[0] * (100 + stop) / 100, p_precision
                    )

                if last_channel_range >= channel_range:
                    grid_type = 0

                    if close[i] <= fibo_levels[0] and close[i] > fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[2], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                    elif close[i] <= fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )

                    qty_take_1[0] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[0] / 100, q_precision
                    )
                    qty_take_1[1] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[1] / 100, q_precision
                    )
                    qty_take_1[2] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[2] / 100, q_precision
                    )
                    qty_take_1[3] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[3] / 100, q_precision
                    )
                    qty_take_1[4] = round_to_minqty_or_mintick(
                        position_size * take_volume_1[4] / 100, q_precision
                    )
                    alert_short_1 = True
                elif last_channel_range < channel_range:
                    grid_type = 1

                    if close[i] <= fibo_levels[0] and close[i] > fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[2], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[5][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )
                        take_price[6][i] = round_to_minqty_or_mintick(
                            fibo_levels[8], p_precision
                        )
                        take_price[7][i] = round_to_minqty_or_mintick(
                            fibo_levels[9], p_precision
                        )
                        take_price[8][i] = round_to_minqty_or_mintick(
                            fibo_levels[10], p_precision
                        )
                        take_price[9][i] = round_to_minqty_or_mintick(
                            fibo_levels[11], p_precision
                        )
                    elif close[i] <= fibo_levels[1]:
                        take_price[0][i] = round_to_minqty_or_mintick(
                            fibo_levels[3], p_precision
                        )
                        take_price[1][i] = round_to_minqty_or_mintick(
                            fibo_levels[4], p_precision
                        )
                        take_price[2][i] = round_to_minqty_or_mintick(
                            fibo_levels[5], p_precision
                        )
                        take_price[3][i] = round_to_minqty_or_mintick(
                            fibo_levels[6], p_precision
                        )
                        take_price[4][i] = round_to_minqty_or_mintick(
                            fibo_levels[7], p_precision
                        )
                        take_price[5][i] = round_to_minqty_or_mintick(
                            fibo_levels[8], p_precision
                        )
                        take_price[6][i] = round_to_minqty_or_mintick(
                            fibo_levels[9], p_precision
                        )
                        take_price[7][i] = round_to_minqty_or_mintick(
                            fibo_levels[10], p_precision
                        )
                        take_price[8][i] = round_to_minqty_or_mintick(
                            fibo_levels[11], p_precision
                        )
                        take_price[9][i] = round_to_minqty_or_mintick(
                            fibo_levels[12], p_precision
                        )

                    qty_take_2[0] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[0] / 100, q_precision
                    )
                    qty_take_2[1] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[1] / 100, q_precision
                    )
                    qty_take_2[2] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[2] / 100, q_precision
                    )
                    qty_take_2[3] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[3] / 100, q_precision
                    )
                    qty_take_2[4] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[4] / 100, q_precision
                    )
                    qty_take_2[5] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[5] / 100, q_precision
                    )
                    qty_take_2[6] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[6] / 100, q_precision
                    )
                    qty_take_2[7] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[7] / 100, q_precision
                    )
                    qty_take_2[8] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[8] / 100, q_precision
                    )
                    qty_take_2[9] = round_to_minqty_or_mintick(
                        position_size * take_volume_2[9] / 100, q_precision
                    )
                    alert_short_2 = True

        return (
            completed_deals_log,
            open_deals_log,
            stop_price,
            take_price,
            alert_long_1,
            alert_long_2,
            alert_short_1,
            alert_short_2,
            alert_long_new_stop,
            alert_short_new_stop,
            alert_cancel
        )
    
    def trade(self, symbol: str) -> None:
        if not hasattr(self, 'pending_order_ids'):
            self.pending_order_ids = {
                'market_stop_ids': [],
                'limit_ids': [],
            }

        if self.alert_cancel:
            self.client.cancel_all_orders(symbol)

        order_ids = self.client.check_stop_orders(
            symbol=symbol,
            order_ids=self.pending_order_ids['market_stop_ids']
        )

        if order_ids:
            self.pending_order_ids['market_stop_ids'] = order_ids

        order_ids = self.client.check_limit_orders(
            symbol=symbol,
            order_ids=self.pending_order_ids['limit_ids']
        )

        if order_ids:
            self.pending_order_ids['limit_ids'] = order_ids

        if self.alert_long_new_stop:
            self.client.cancel_stop(
                symbol=symbol, 
                side='Sell'
            )

            order_ids = self.client.check_stop_orders(
                symbol=symbol,
                order_ids=self.pending_order_ids['market_stop_ids']
            )

            if order_ids:
                self.pending_order_ids['market_stop_ids'] = order_ids

            order_id = self.client.market_stop_sell(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

        if self.alert_short_new_stop:
            self.client.cancel_stop(
                symbol=symbol, 
                side='Buy'
            )

            order_ids = self.client.check_stop_orders(
                symbol=symbol,
                order_ids=self.pending_order_ids['market_stop_ids']
            )

            if order_ids:
                self.pending_order_ids['market_stop_ids'] = order_ids

            order_id = self.client.market_stop_buy(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

        if self.alert_long_1:
            self.client.market_open_buy(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=self.leverage,
                hedge=False
            )
            order_id = self.client.market_stop_sell(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_1[0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_1[1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_1[2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_1[3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

        if self.alert_long_2:
            self.client.market_open_buy(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=self.leverage,
                hedge=False
            )
            order_id = self.client.market_stop_sell(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[4]}%',
                price=self.take_price[4][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[5]}%',
                price=self.take_price[5][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[6]}%',
                price=self.take_price[6][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[7]}%',
                price=self.take_price[7][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume_2[8]}%',
                price=self.take_price[8][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_sell(
                symbol=symbol,
                size='100%',
                price=self.take_price[9][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

        if self.alert_short_1:
            self.client.market_open_sell(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=self.leverage,
                hedge=False
            )
            order_id = elf.client.market_stop_buy(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_1[0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_1[1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_1[2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_1[3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

        if self.alert_short_2:
            self.client.market_open_sell(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=self.leverage,
                hedge=False
            )
            order_id = self.client.market_stop_buy(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.pending_order_ids['market_stop_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[0]}%',
                price=self.take_price[0][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[1]}%',
                price=self.take_price[1][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[2]}%',
                price=self.take_price[2][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[3]}%',
                price=self.take_price[3][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[4]}%',
                price=self.take_price[4][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[5]}%',
                price=self.take_price[5][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[6]}%',
                price=self.take_price[6][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[7]}%',
                price=self.take_price[7][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume_2[8]}%',
                price=self.take_price[8][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=symbol,
                size='100%',
                price=self.take_price[9][-1],
                hedge=False
            )

            if order_id:
                self.pending_order_ids['limit_ids'].append(order_id)