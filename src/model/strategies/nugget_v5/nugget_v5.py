import random as rand

import numpy as np
import numba as nb

import src.model.ta as ta
import src.model.math as math
from src.model.strategies.strategy import Strategy


class NuggetV5(Strategy):
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
    opt_params = {
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
            math.get_random_volumes(5, 10, 10)
            for _ in range(1000)
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
        'opt_params',
        'indicator_options',
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
        for key, value in NuggetV5.__dict__.items():
            if (not key.startswith('__') and
                    key not in NuggetV5.class_attributes):
                self.__dict__[key] = value

        if opt_params is not None:
            self.stop = opt_params[0]
            self.atr_length = opt_params[1]
            self.take_value = opt_params[2]
            self.take_volume = opt_params[3]
            self.st_atr_period = opt_params[4]
            self.st_factor = opt_params[5]
            self.st_upper_limit = opt_params[6]
            self.st_lower_limit = opt_params[7]
            self.k_length = opt_params[8]
            self.d_length = opt_params[9]
            self.k_d_long_limit = opt_params[10]
            self.k_d_short_limit = opt_params[11]
            self.adx_filter = opt_params[12]
            self.di_length = opt_params[13]
            self.adx_length = opt_params[14]
            self.adx_long_upper_limit = opt_params[15]
            self.adx_long_lower_limit = opt_params[16]
            self.adx_short_upper_limit = opt_params[17]
            self.adx_short_lower_limit = opt_params[18]

        if all_params is not None:
            self.margin_type = all_params[0]
            self.direction = all_params[1]
            self.initial_capital = all_params[2]
            self.min_capital = all_params[3]
            self.commission = all_params[4]
            self.order_size_type = all_params[5]
            self.order_size = all_params[6]
            self.leverage = all_params[7]
            self.stop = all_params[8]
            self.atr_length = all_params[9]
            self.take_value = all_params[10]
            self.take_volume = all_params[11]
            self.st_atr_period = all_params[12]
            self.st_factor = all_params[13]
            self.st_upper_limit = all_params[14]
            self.st_lower_limit = all_params[15]
            self.k_length = all_params[16]
            self.d_length = all_params[17]
            self.k_d_long_limit = all_params[18]
            self.k_d_short_limit = all_params[19]
            self.adx_filter = all_params[20]
            self.di_length = all_params[21]
            self.adx_length = all_params[22]
            self.adx_long_upper_limit = all_params[23]
            self.adx_long_lower_limit = all_params[24]
            self.adx_short_upper_limit = all_params[25]
            self.adx_short_lower_limit = all_params[26]

    def start(self, exchange_data: dict) -> None:
        super().__init__()
        
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
                np.full(self.time.shape[0], np.nan)
            ]
        )
        self.liquidation_price = np.nan
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
        nb.types.Tuple((
            nb.float64[:],
            nb.float64[:],
            nb.float64[:, :],
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
        direction: int,
        initial_capital: float,
        min_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop: float,
        take_value: list,
        take_volume: list,
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
        deal_type: float,
        entry_signal: float,
        entry_date: float,
        entry_price: float,
        liquidation_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        position_size: float,
        qty_take: np.ndarray,
        atr: np.ndarray,
        ds_upper_band: np.ndarray,
        ds_lower_band: np.ndarray,
        st_upper_band_changed: np.ndarray,
        st_lower_band_changed: np.ndarray,
        k: np.ndarray,
        d: np.ndarray,
        adx: np.ndarray,
        alert_long: bool,
        alert_short: bool,
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
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                stop_price[i] = round_to_minqty_or_mintick(
                    ds_lower_band[i] * (100 - stop) / 100, p_precision
                )
                take_price[0][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[0] * atr[i], p_precision
                )
                take_price[1][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[1] * atr[i], p_precision
                )
                take_price[2][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[2] * atr[i], p_precision
                )
                take_price[3][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[3] * atr[i], p_precision
                )
                take_price[4][i] = round_to_minqty_or_mintick(
                    close[i] + take_value[4] * atr[i], p_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, q_precision
                )
                qty_take[0] = round_to_minqty_or_mintick(
                    position_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = round_to_minqty_or_mintick(
                    position_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = round_to_minqty_or_mintick(
                    position_size * take_volume[2] / 100, q_precision
                )
                qty_take[3] = round_to_minqty_or_mintick(
                    position_size * take_volume[3] / 100, q_precision
                )
                qty_take[4] = round_to_minqty_or_mintick(
                    position_size * take_volume[4] / 100, q_precision
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
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                stop_price[i] = round_to_minqty_or_mintick(
                    ds_upper_band[i] * (100 + stop) / 100, p_precision
                )
                take_price[0][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[0] * atr[i], p_precision
                )
                take_price[1][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[1] * atr[i], p_precision
                )
                take_price[2][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[2] * atr[i], p_precision
                )
                take_price[3][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[3] * atr[i], p_precision
                )
                take_price[4][i] = round_to_minqty_or_mintick(
                    close[i] - take_value[4] * atr[i], p_precision
                )
                position_size = round_to_minqty_or_mintick(
                    position_size, q_precision
                )
                qty_take[0] = round_to_minqty_or_mintick(
                    position_size * take_volume[0] / 100, q_precision
                )
                qty_take[1] = round_to_minqty_or_mintick(
                    position_size * take_volume[1] / 100, q_precision
                )
                qty_take[2] = round_to_minqty_or_mintick(
                    position_size * take_volume[2] / 100, q_precision
                )
                qty_take[3] = round_to_minqty_or_mintick(
                    position_size * take_volume[3] / 100, q_precision
                )
                qty_take[4] = round_to_minqty_or_mintick(
                    position_size * take_volume[4] / 100, q_precision
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
    
    def trade(self, symbol: str) -> None:
        if self.alert_cancel:
            self.client.futures_cancel_all_orders(symbol)

        self.client.check_stop_status(symbol)
        self.client.check_limit_status(symbol)

        if self.alert_long_new_stop:
            self.client.futures_cancel_stop(
                symbol=symbol, 
                side='Sell'
            )
            self.client.check_stop_status(symbol)
            self.client.futures_market_stop_sell(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
        
        if self.alert_short_new_stop:
            self.client.futures_cancel_stop(
                symbol=symbol, 
                side='Buy'
            )
            self.client.check_stop_status(symbol)
            self.client.futures_market_stop_buy(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )

        if self.alert_long:
            self.client.futures_market_open_buy(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=str(self.leverage),
                hedge='false'
            )
            self.client.futures_market_stop_sell(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume[0]}%',
                price=self.take_price[0][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume[1]}%',
                price=self.take_price[1][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume[2]}%',
                price=self.take_price[2][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=symbol,
                size=f'{self.take_volume[3]}%',
                price=self.take_price[3][-1],
                hedge='false'
            )
            self.client.futures_limit_take_sell(
                symbol=symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge='false'
            )
        
        if self.alert_short:
            self.client.futures_market_open_sell(
                symbol=symbol,
                size=(
                    f'{self.order_size}'
                    f'{'%' if self.order_size_type == 0 else 'u'}'
                ),
                margin=('isolated' if self.margin_type == 0 else 'cross'),
                leverage=str(self.leverage),
                hedge='false'
            )
            self.client.futures_market_stop_buy(
                symbol=symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume[0]}%',
                price=self.take_price[0][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume[1]}%',
                price=self.take_price[1][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume[2]}%',
                price=self.take_price[2][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=symbol,
                size=f'{self.take_volume[3]}%',
                price=self.take_price[3][-1],
                hedge='false'
            )
            self.client.futures_limit_take_buy(
                symbol=symbol,
                size='100%',
                price=self.take_price[4][-1],
                hedge='false'
            )