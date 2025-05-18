import numpy as np
import numba as nb

import src.core.lib.ta as ta
from src.core.strategy.base_strategy import BaseStrategy


class DickeyFullerV1(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes

    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    # direction: 0 - "all", 1 — "longs", 2 — "shorts"

    params = {
        "margin_type": 0,
        "direction": 0,
        "initial_capital": 10000.0,
        "commission": 0.05,
        "leverage_p1": 1,
        "order_size_p1": 100.0,
        "leverage_p2": 1,
        "order_size_p2": 50.0,
        "stop_loss_p1": 11.9,
        "ema_length_p1": 77,
        "adf_length_1_p1": 26,
        "adf_length_2_p1": 7,
        "n_lag_1_p1": 1,
        "n_lag_2_p1": 2,
        "adf_level_1_p1": 0.7,
        "adf_level_2_p1": -1.0,
        "stop_loss_p2": 7.5,
        "take_profit_p2": 11.8,
        "entry_bar_p2": 1,
        "ema_length_p2": 148,
        "bb_length_p2": 11,
        "bb_mult_p2": 1.3,
        "adf_length_1_p2": 25,
        "adf_length_2_p2": 53,
        "n_lag_1_p2": 2,
        "n_lag_2_p2": 0,
        "adf_level_1_p2": 1.5,
        "adf_level_2_p2": 1.1
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_loss_p1': [i / 10 for i in range(10, 151)],
        'ema_length_p1': [i for i in range(15, 201)],
        'adf_length_1_p1': [i for i in range(7, 201)],
        'adf_length_2_p1': [i for i in range(7, 201)],
        'n_lag_1_p1': [i for i in range(0, 3)],
        'n_lag_2_p1': [i for i in range(0, 3)],
        'adf_level_1_p1': [i / 10 for i in range(0, 21)],
        'adf_level_2_p1': [i / 10 for i in range(-10, 21)],
        'stop_loss_p2': [i / 10 for i in range(10, 101)],
        'take_profit_p2': [i / 10 for i in range(30, 301, 2)],
        'entry_bar_p2': [i for i in range(0, 2)],
        'ema_length_p2': [i for i in range(15, 201)],
        'bb_length_p2': [i for i in range(10, 31)],
        'bb_mult_p2': [i / 10 for i in range(5, 51)],
        'adf_length_1_p2': [i for i in range(7, 201)],
        'adf_length_2_p2': [i for i in range(7, 201)],
        'n_lag_1_p2': [i for i in range(0, 3)],
        'n_lag_2_p2': [i for i in range(0, 3)],
        'adf_level_1_p2': [i / 10 for i in range(0, 21)],
        'adf_level_2_p2': [i / 10 for i in range(-10, 21)]
    }

    # For frontend
    indicator_options = {
        'SL': {'color': '#FF0000'},
        'TP': {'color': '#008000'}
    }

    def __init__(self, all_params = None, opt_params = None) -> None:
        super().__init__(all_params=all_params, opt_params=opt_params)

    def start(self, client, market_data) -> None:
        self.open_deals_log = np.full(5, np.nan)
        self.completed_deals_log = np.array([])
        self.position_size = np.nan
        self.entry_signal = np.nan
        self.entry_price = np.nan
        self.entry_date = np.nan
        self.deal_type = np.nan

        self.client = client
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
        self.entry_short_stage_p2 = np.nan

        self.adf_1_p1 = ta.adftest(
            source=self.close,
            length=self.params['adf_length_1_p1'],
            lags=self.params['n_lag_1_p1']
        )
        self.adf_2_p1 = ta.adftest(
            source=self.close,
            length=self.params['adf_length_2_p1'],
            lags=self.params['n_lag_2_p1']
        )
        self.adf_1_p2 = ta.adftest(
            source=self.close,
            length=self.params['adf_length_1_p2'],
            lags=self.params['n_lag_1_p2']
        )
        self.adf_2_p2 = ta.adftest(
            source=self.close,
            length=self.params['adf_length_2_p2'],
            lags=self.params['n_lag_2_p2']
        )
        self.ema_p1 = ta.ema(
            source=self.close,
            length=self.params['ema_length_p1']
        )
        self.ema_p2 = ta.ema(
            source=self.close,
            length=self.params['ema_length_p2']
        )
        self.bb = ta.bb(
            source=self.close,
            length=self.params['bb_length_p2'],
            mult=self.params['bb_mult_p2']
        )
        self.bb_upper_p2 = self.bb[1]
        self.bb_lower_p2 = self.bb[2]

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
                self.params['leverage_p1'],
                self.params['order_size_p1'],
                self.params['leverage_p2'],
                self.params['order_size_p2'],
                self.params['stop_loss_p1'],
                self.params['adf_level_1_p1'],
                self.params['adf_level_2_p1'],
                self.params['stop_loss_p2'],
                self.params['take_profit_p2'],
                self.params['entry_bar_p2'],
                self.params['adf_level_1_p2'],
                self.params['adf_level_2_p2'],
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
                self.entry_short_stage_p2,
                self.adf_1_p1,
                self.adf_2_p1,
                self.adf_1_p2,
                self.adf_2_p2,
                self.ema_p1,
                self.ema_p2,
                self.bb_upper_p2,
                self.bb_lower_p2,
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
        leverage_p1: int,
        order_size_p1: float,
        leverage_p2: int,
        order_size_p2: float,
        stop_loss_p1: float,
        adf_level_1_p1: float,
        adf_level_2_p1: float,
        stop_loss_p2: float,
        take_profit_p2: float,
        entry_bar_p2: int,
        adf_level_1_p2: float,
        adf_level_2_p2: float,
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
        entry_short_stage_p2: float,
        adf_1_p1: np.ndarray,
        adf_2_p1: np.ndarray,
        adf_1_p2: np.ndarray,
        adf_2_p2: np.ndarray,
        ema_p1: np.ndarray,
        ema_p2: np.ndarray,
        bb_upper_p2: np.ndarray,
        bb_lower_p2: np.ndarray,
        alert_entry_long: bool,
        alert_exit_long: bool,
        alert_entry_short: bool,
        alert_exit_short: bool,
        alert_cancel: bool
    ) -> tuple:
        def round_step(number: float, precision: float) -> float:
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
            alert_entry_long = False
            alert_exit_long = False
            alert_entry_short = False
            alert_exit_short = False
            alert_cancel = False

            if i > 0:
                stop_price[i] = stop_price[i - 1]
                take_price[i] = take_price[i - 1]

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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
                entry_short_stage_p2 = np.nan
                alert_cancel = True

            # Exit long
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
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    position_size = np.nan
                    alert_cancel = True

            exit_long = (
                close[i] < ema_p1[i] and
                close[i] < open[i] and
                adf_2_p1[i] > adf_level_2_p1 and
                deal_type == 0
            )

            if exit_long:
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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                position_size = np.nan
                alert_exit_long = True
                alert_cancel = True

            # Exit short
            if deal_type == 1:
                if high[i] - open[i] >= open[i] - low[i]:
                    if low[i] <= take_price[i]:
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
                        liquidation_price = np.nan
                        take_price[i] = np.nan
                        stop_price[i] = np.nan
                        position_size = np.nan
                        entry_short_stage_p2 = np.nan
                        alert_cancel = True
                    elif high[i] >= stop_price[i]:
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
                        take_price[i] = np.nan
                        stop_price[i] = np.nan
                        position_size = np.nan
                        entry_short_stage_p2 = np.nan
                        alert_cancel = True
                else:
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
                        take_price[i] = np.nan
                        stop_price[i] = np.nan
                        position_size = np.nan
                        entry_short_stage_p2 = np.nan
                        alert_cancel = True
                    elif low[i] <= take_price[i]:
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
                        liquidation_price = np.nan
                        take_price[i] = np.nan
                        stop_price[i] = np.nan
                        position_size = np.nan
                        entry_short_stage_p2 = np.nan
                        alert_cancel = True

            exit_short = (
                close[i] > ema_p2[i] and
                close[i] > open[i] and
                adf_2_p2[i] > adf_level_2_p2 and
                deal_type == 1
            )

            if exit_short:
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
                entry_short_stage_p2 = np.nan
                alert_exit_short = True
                alert_cancel = True

            # Entry long
            entry_long = (
                close[i] > open[i] and
                close[i] > ema_p1[i] and
                adf_1_p1[i] > adf_level_1_p1 and
                (direction == 0 or direction == 1) and
                deal_type != 0
            )

            if entry_long:
                if deal_type == 1:
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
                    entry_short_stage_p2 = np.nan
                    alert_exit_short = True
                    alert_cancel = True

                deal_type = 0
                entry_signal = 0
                entry_price = close[i]
                initial_position =  (
                    equity * leverage_p1 * (order_size_p1 / 100.0)
                )
                position_size = round_step(
                    initial_position * (1 - commission / 100) / entry_price,
                    q_precision
                )
                entry_date = time[i]
                liquidation_price = round_step(
                    entry_price * (1 - 1 / leverage_p1),
                    p_precision
                )
                stop_price[i] = round_step(
                    close[i] * (100 - stop_loss_p1) / 100,
                    p_precision
                )
                open_deals_log = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, position_size
                    ]
                )
                alert_entry_long = True

            # Entry short
            if np.isnan(entry_short_stage_p2) and close[i] > ema_p2[i]:
                entry_short_stage_p2 = 1

            if (entry_short_stage_p2 == 1 and
                    close[i] < ema_p2[i] and
                    adf_1_p2[i] > adf_level_1_p2 and
                    (direction == 0 or direction == 2) and
                    np.isnan(deal_type)):
                entry_short_stage_p2 = 2

            if (np.isnan(deal_type) and
                    entry_short_stage_p2 == 2 and
                    close[i] < bb_upper_p2[i] and
                    close[i] > bb_lower_p2[i] and
                    (True if entry_bar_p2 == 0 else close[i] > open[i])):
                entry_short_stage_p2 = 3

            if entry_short_stage_p2 == 3:
                deal_type = 1
                entry_signal = 1
                entry_price = close[i]
                initial_position =  (
                    equity * leverage_p2 * (order_size_p2 / 100.0)
                )
                position_size = round_step(
                    initial_position * (1 - commission / 100) / entry_price,
                    q_precision
                )
                entry_date = time[i]
                liquidation_price = round_step(
                    entry_price * (1 + 1 / leverage_p2),
                    p_precision
                )
                stop_price[i] = round_step(
                    close[i] * (100 + stop_loss_p2) / 100,
                    p_precision
                )
                take_price[i] = round_step(
                    close[i] * (100 - take_profit_p2) / 100,
                    p_precision
                )
                entry_short_stage_p2 = np.nan
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
            self.client.market_close_sell(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_exit_short:
            self.client.market_close_buy(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_entry_long:
            self.client.market_open_buy(
                symbol=self.symbol,
                size=f'{self.params['order_size_p1']}%',
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage_p1'],
                hedge=False
            )
            order_id = self.client.market_stop_sell(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

        if self.alert_entry_short:
            self.client.market_open_sell(
                symbol=self.symbol,
                size=f'{self.params['order_size_p2']}%',
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage_p2'],
                hedge=False
            )
            order_id = self.client.market_stop_buy(
                symbol=self.symbol, 
                size='100%',
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = self.client.limit_take_buy(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        self.cache.save(self.symbol, self.order_ids)