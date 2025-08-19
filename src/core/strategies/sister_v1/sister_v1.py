from typing import TYPE_CHECKING

import numpy as np
import numba as nb

import src.core.quantklines as qk
from src.core.strategy.base_strategy import BaseStrategy
from src.core.strategy.deal_logger import update_completed_deals_log
from src.shared.constants import colors
from src.shared.utils import adjust

if TYPE_CHECKING:
    from src.infrastructure.exchanges import BaseExchangeClient


class SisterV1(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes
    # take_type: 0 — "fixed", 1 — "trailing"
    params = {
        "stop": 10.0,
        "take_type": 1,
        "take": 10.0,
        "length_entry": 35,
        "ratio_entry": 5.0,
        "length_exit": 35,
        "ratio_exit": 1.0,
        "length_small_trend": 7,
        "length_medium_trend": 35
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop': [i / 2 for i in range(1, 21)],
        'take': [i / 2 for i in range(1, 31)],
        'length_entry': [i for i in range(10, 61)],
        'ratio_entry': [i / 10 for i in range(5, 51, 5)],
        'length_exit': [i for i in range(5, 105, 5)],
        'ratio_exit': [i / 4 for i in range(0, 13)],
        'length_small_trend': [i for i in range(3, 21)],
        'length_medium_trend': [i for i in range(25, 135, 5)]
    }

    # Frontend rendering settings for indicators
    indicator_options = {
        'SL': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON,
            'lineWidth': 2
        },
        'TP': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN,
            'lineWidth': 2
        },
        'SMA ST': {
            'pane': 0,
            'type': 'line',
            'color': colors.BLUE_VIOLET,
            'lineWidth': 1
        },
        'SMA MT': {
            'pane': 0,
            'type': 'line',
            'color': colors.INDIGO,
            'lineWidth': 1
        },
        'SMA L Entry': {
            'pane': 0,
            'type': 'line',
            'color': colors.CORAL,
            'lineWidth': 1
        },
        'SMA L Exit': {
            'pane': 0,
            'type': 'line',
            'color': colors.PALE_GOLDENROD,
            'lineWidth': 1
        },
        'SMA S Entry': {
            'pane': 0,
            'type': 'line',
            'color': colors.DEEP_SKY_BLUE,
            'lineWidth': 1
        },
        'SMA S Exit': {
            'pane': 0,
            'type': 'line',
            'color': colors.TEAL,
            'lineWidth': 1
        }
    }

    def __init__(
        self,
        client: 'BaseExchangeClient',
        params: dict | None = None
    ) -> None:
        super().__init__(client, params)

    def calculate(self, market_data) -> None:
        super().init_variables(market_data)

        self.take_price = np.full(self.time.shape[0], np.nan)
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.liquidation_price = np.nan

        self.atr_entry = qk.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['length_entry']
        )
        self.sma_entry = qk.sma(
            source=self.close,
            length=self.params['length_entry']
        )
        self.sma_long_entry = (
            self.sma_entry -
            self.atr_entry * self.params['ratio_entry']
        )
        self.sma_short_entry = (
            self.sma_entry +
            self.atr_entry * self.params['ratio_entry']
        )

        self.atr_exit = qk.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['length_exit']
        )
        self.sma_exit = qk.sma(
            source=self.close,
            length=self.params['length_exit']
        )
        self.sma_long_exit = (
            self.sma_exit +
            self.atr_exit * self.params['ratio_exit']
        )
        self.sma_short_exit = (
            self.sma_exit -
            self.atr_exit * self.params['ratio_exit']
        )

        self.sma_small_trend = qk.sma(
            source=self.close,
            length=self.params['length_small_trend']
        )
        self.sma_medium_trend = qk.sma(
            source=self.close,
            length=self.params['length_medium_trend']
        )

        self.cond_exit_long = qk.crossover(
            source1=self.close,
            source2=self.sma_long_exit
        )
        self.cond_exit_short = qk.crossover(
            source1=self.close,
            source2=self.sma_short_exit
        )

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_close_long = False
        self.alert_close_short = False
        self.alert_long_new_take = False
        self.alert_short_new_take = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.take_price,
            self.stop_price,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short,
            self.alert_long_new_take,
            self.alert_short_new_take
        ) = self._calculate_loop(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['commission'],
            self.params['position_size_type'],
            self.params['position_size'],
            self.params['leverage'],
            self.params['stop'],
            self.params['take_type'],
            self.params['take'],
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
            self.position_type,
            self.order_signal,
            self.order_date,
            self.order_price,
            self.take_price,
            self.stop_price,
            self.liquidation_price,
            self.order_size,
            self.sma_long_entry,
            self.sma_short_entry,
            self.sma_long_exit,
            self.sma_short_exit,
            self.sma_small_trend,
            self.sma_medium_trend,
            self.cond_exit_long,
            self.cond_exit_short,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short,
            self.alert_long_new_take,
            self.alert_short_new_take
        )

        self.indicators = {
            'SL': {
                'options': self.indicator_options['SL'],
                'values': self.stop_price
            },
            'TP': {
                'options': self.indicator_options['TP'],
                'values': self.take_price
            },
            'SMA ST': {
                'options': self.indicator_options['SMA ST'],
                'values': self.sma_small_trend
            },
            'SMA MT': {
                'options': self.indicator_options['SMA MT'],
                'values': self.sma_medium_trend
            },
            'SMA L Entry': {
                'options': self.indicator_options['SMA L Entry'],
                'values': self.sma_long_entry
            },
            'SMA L Exit': {
                'options': self.indicator_options['SMA L Exit'],
                'values': self.sma_long_exit
            },
            'SMA S Entry': {
                'options': self.indicator_options['SMA S Entry'],
                'values': self.sma_short_entry
            },
            'SMA S Exit': {
                'options': self.indicator_options['SMA S Exit'],
                'values': self.sma_short_exit
            }
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        direction: int,
        initial_capital: float,
        commission: float,
        position_size_type: int,
        position_size: float,
        leverage: int,
        stop: float,
        take_type: int,
        take: float,
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
        position_type: float,
        order_signal: float,
        order_date: float,
        order_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        liquidation_price: float,
        order_size: float,
        sma_long_entry: np.ndarray,
        sma_short_entry: np.ndarray,
        sma_long_exit: np.ndarray,
        sma_short_exit: np.ndarray,
        sma_small_trend: np.ndarray,
        sma_medium_trend: np.ndarray,
        cond_exit_long: np.ndarray,
        cond_exit_short: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_close_long: bool,
        alert_close_short: bool,
        alert_long_new_take: bool,
        alert_short_new_take: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_price[i] = take_price[i - 1]

            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_close_long = False
            alert_close_short = False
            alert_long_new_take = False
            alert_short_new_take = False

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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
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
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                alert_cancel = True

            # Trading logic (longs)
            is_new_take_price = (
                take_type == 1 and
                position_type == 0 and
                not np.isnan(take_price[i - 1])
            )

            if is_new_take_price:
                take_price[i] = min(sma_long_exit[i], take_price[i - 1])
                alert_long_new_take = True

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
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    alert_cancel = True

                if high[i] >= take_price[i]:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        300,
                        order_date,
                        time[i],
                        order_price,
                        take_price[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    alert_cancel = True

            exit_long = (
                position_type == 0 and
                cond_exit_long[i]
            )
            entry_long = (
                np.isnan(position_type) and
                high[i - 1] >= sma_long_entry[i - 1] and
                low[i - 1] <= sma_long_entry[i - 1] and
                close[i] > close[i - 1] and
                close[i] > open[i] and
                close[i] > sma_small_trend[i] and
                close[i] > sma_medium_trend[i] and
                close[i] < sma_long_exit[i] and
                (direction == 0 or direction == 1)
            )

            if exit_long:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    100,
                    order_date,
                    time[i],
                    order_price,
                    close[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                alert_close_long = True
                alert_cancel = True

            if entry_long:
                position_type = 0
                order_signal = 100
                order_date = time[i]
                order_price = close[i]

                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = adjust(
                        initial_position * (1 - commission / 100)
                        / order_price, q_precision
                    )
                else:
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = adjust(
                        initial_position * (1 - commission / 100)
                        / order_price, q_precision
                    )

                take_price[i] = adjust(
                    order_price * (100 + take) / 100, p_precision
                )
                stop_price[i] = adjust(
                    order_price * (100 - stop) / 100, p_precision
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
                alert_open_long = True

            # Trading logic (shorts)
            is_new_take_price = (
                take_type == 1 and
                position_type == 1 and
                not np.isnan(take_price[i - 1])
            )

            if is_new_take_price:
                take_price[i] = max(sma_short_exit[i], take_price[i - 1])
                alert_short_new_take = True

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
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    alert_cancel = True 

                if low[i] <= take_price[i]:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        400,
                        order_date,
                        time[i],
                        order_price,
                        take_price[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    liquidation_price = np.nan
                    order_size = np.nan
                    alert_cancel = True 

            exit_short = (
                position_type == 1 and
                cond_exit_short[i]
            )
            entry_short = (
                np.isnan(position_type) and
                high[i - 1] >= sma_short_entry[i - 1] and
                low[i - 1] <= sma_short_entry[i - 1] and
                close[i] < close[i - 1] and
                close[i] < open[i] and
                close[i] < sma_small_trend[i] and
                close[i] < sma_medium_trend[i] and
                close[i] > sma_short_exit[i] and
                (direction == 0 or direction == 2)
            )

            if exit_short:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    200,
                    order_date,
                    time[i],
                    order_price,
                    close[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                alert_close_short = True
                alert_cancel = True

            if entry_short:
                position_type = 1
                order_signal = 200
                order_date = time[i]
                order_price = close[i]

                if position_size_type == 0:
                    initial_position = (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = adjust(
                        initial_position * (1 - commission / 100)
                        / order_price, q_precision
                    )
                else:
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = adjust(
                        initial_position * (1 - commission / 100)
                        / order_price, q_precision
                    )

                take_price[i] = adjust(
                    order_price * (100 - take) / 100, p_precision
                )
                stop_price[i] = adjust(
                    order_price * (100 + stop) / 100, p_precision
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
                alert_open_short = True

        return (
            completed_deals_log,
            open_deals_log,
            take_price,
            stop_price,
            alert_cancel,
            alert_open_long,
            alert_open_short,
            alert_close_long,
            alert_close_short,
            alert_long_new_take,
            alert_short_new_take
        )

    def _trade(self) -> None:
        if self.alert_cancel:
            self.client.trade.cancel_all_orders(self.symbol)

        self.order_ids['stop_ids'] = self.client.trade.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )
        self.order_ids['limit_ids'] = self.client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_long_new_take:
            self.client.trade.cancel_limit_orders(
                symbol=self.symbol,
                side='sell'
            )
            self.order_ids['limit_ids'] = self.client.trade.check_limit_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['limit_ids']
            )
            order_id = self.client.trade.limit_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.take_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_short_new_take:
            self.client.trade.cancel_limit_orders(
                symbol=self.symbol,
                side='buy'
            )
            self.order_ids['limit_ids'] = self.client.trade.check_limit_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['limit_ids']
            )
            order_id = self.client.trade.limit_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.take_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_close_long:
            self.client.trade.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_close_short:
            self.client.trade.market_close_short(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_open_long:
            self.client.trade.market_open_long(
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
            order_id = self.client.trade.market_stop_close_long(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = self.client.trade.limit_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        if self.alert_open_short:
            self.client.trade.market_open_short(
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
            order_id = self.client.trade.market_stop_close_short(
                symbol=self.symbol, 
                size='100%', 
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = self.client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)