import numpy as np
import numba as nb

from . import (
    BaseStrategy,
    Interval,
    adjust,
    colors,
    quanta,
    log
)


class ExampleV2(BaseStrategy):
    # --- Strategy Configuration ---
    # Default parameter values for backtesting and live trading
    params = {
        'position_size':  50,
        'entry_volume_1': 10.0,
        'entry_volume_2': 15.0,
        'entry_volume_3': 25.0,
        'entry_volume_4': 50.0,
        'entry_percent_2': 2.0,
        'entry_percent_3': 6.0,
        'entry_percent_4': 8.0,
        'take_profit': 1.0,
        'lookback': 1,
        'ma_length': 20,
        'mult': 2.0,
        'range_threshold': 30.0,
    }

    # --- Optimization Space ---
    # Parameter ranges for hyperparameter optimization
    opt_params = {
        'entry_percent_2': [i / 10 for i in range(20, 101)],
        'entry_percent_3': [i / 10 for i in range(50, 151)],
        'entry_percent_4': [i / 10 for i in range(100, 301)],
        'take_profit': [i / 10 for i in range(10, 201)],
        'lookback': [i for i in range(1, 21)],
        'ma_length': [i for i in range(10, 101)],
        'mult': [i / 10 for i in range(10, 31)],
        'range_threshold': [float(i) for i in range(10, 100)],
    }

    # --- UI/UX Configuration ---
    # Human-readable labels for frontend parameter display
    param_labels = {
        'position_size': 'Position Size',
        'entry_volume_1': 'Entry Volume 1 (%)',
        'entry_volume_2': 'Entry Volume 2 (%)',
        'entry_volume_3': 'Entry Volume 3 (%)',
        'entry_volume_4': 'Entry Volume 4 (%)',
        'entry_percent_2': 'Entry Level 2 (%)',
        'entry_percent_3': 'Entry Level 3 (%)',
        'entry_percent_4': 'Entry Level 4 (%)',
        'take_profit': 'Take Profit (%)',
        'lookback': 'Lookback Bars',
        'ma_length': 'MA Length',
        'mult': 'Multiplier',
        'range_threshold': 'Range Threshold',
    }

    # --- Visualization Settings ---
    # Visualization Settings for technical indicators
    indicator_options = {
        'HTF': {
            'pane': 0,
            'type': 'line',
            'color': colors.RED_600,
        },
        'EP #2': {
            'pane': 0,
            'type': 'line',
            'color': colors.PURPLE_900,
        },
        'EP #3': {
            'pane': 0,
            'type': 'line',
            'color': colors.PURPLE_900,
        },
        'EP #4': {
            'pane': 0,
            'type': 'line',
            'color': colors.PURPLE_900,
        },
        'TP': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN_800,
        },
    }

    # --- Data Feed Configuration ---
    # Market data sources required for strategy calculations
    feeds = {
        'klines': {
            'HTF': ['symbol', Interval.DAY_1],
        },
    }

    def calculate(self) -> None:
        # Entry price levels
        self.entry_price_2 = np.full(self.time.shape[0], np.nan)
        self.entry_price_3 = np.full(self.time.shape[0], np.nan)
        self.entry_price_4 = np.full(self.time.shape[0], np.nan)

        # Exit price levels
        self.take_price = np.full(self.time.shape[0], np.nan)
        self.liquidation_price = np.nan

        # Quantity management
        self.entry_volumes = np.array([
            self.params['entry_volume_1'],
            self.params['entry_volume_2'],
            self.params['entry_volume_3'],
            self.params['entry_volume_4'],
        ])
        self.qty_entry = np.full(4, np.nan)

        # Technical indicators
        self.lowest = quanta.lowest(
            source=np.roll(self.low, 1),
            length=self.params['lookback']
        )
        self.sma = quanta.sma(
            source=(self.high - self.low), 
            length=self.params['ma_length']
        )

        # Additional market data
        self.htf_close = np.full(self.time.shape[0], np.nan)

        if len(self.feeds_data['klines']['HTF']['close'].shape) == 1:
            self.htf_close = self.feeds_data['klines']['HTF']['close']

        # Alert flags for signals
        self.alert_open_long = False
        self.alert_close_long = False

        # Main calculation loop (Numba-optimized)
        (
            self.completed_deals_log,
            self.open_deals_log,
            self.entry_price_2,
            self.entry_price_3,
            self.entry_price_4,
            self.take_price,
            self.alert_open_long,
            self.alert_close_long
        ) = self._calculate_loop(
            self.params['initial_capital'],
            self.params['commission'],
            self.params['position_size_type'],
            self.params['position_size'],
            self.params['leverage'],
            self.params['entry_percent_2'],
            self.params['entry_percent_3'],
            self.params['entry_percent_4'],
            self.params['take_profit'],
            self.params['mult'],
            self.params['range_threshold'],
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
            self.order_signal,
            self.order_price,
            self.order_date,
            self.order_size,
            self.position_type,
            self.take_price,
            self.liquidation_price,
            self.qty_entry,
            self.entry_price_2,
            self.entry_price_3,
            self.entry_price_4,
            self.entry_volumes,
            self.lowest,
            self.sma,
            self.alert_open_long,
            self.alert_close_long
        )

        # Visualization indicators
        self.indicators = {
            'HTF': {
                'options': self.indicator_options['HTF'],
                'values': self.htf_close,
            },
            'EP #2': {
                'options': self.indicator_options['EP #2'],
                'values': self.entry_price_2,
            },
            'EP #3': {
                'options': self.indicator_options['EP #3'],
                'values': self.entry_price_3,
            },
            'EP #4': {
                'options': self.indicator_options['EP #4'],
                'values': self.entry_price_4,
            },
            'TP': {
                'options': self.indicator_options['TP'],
                'values': self.take_price,
            },
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        initial_capital: float,
        commission: float,
        position_size_type: int,
        position_size: float,
        leverage: int,
        entry_percent_2: float,
        entry_percent_3: float,
        entry_percent_4: float,
        take_profit: float,
        mult: float,
        range_threshold: float,
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
        order_signal: float,
        order_price: float,
        order_date: float,
        order_size: float,
        position_type: float,
        take_price: np.ndarray,
        liquidation_price: float,
        qty_entry: np.ndarray,
        entry_price_2: np.ndarray,
        entry_price_3: np.ndarray,
        entry_price_4: np.ndarray,
        entry_volumes: np.ndarray,
        lowest: np.ndarray,
        sma: np.ndarray,
        alert_open_long: bool,
        alert_close_long: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            take_price[i] = take_price[i - 1]
            entry_price_2[i] = entry_price_2[i - 1]
            entry_price_3[i] = entry_price_3[i - 1]
            entry_price_4[i] = entry_price_4[i - 1]

            # Reset alerts
            alert_open_long = False
            alert_close_long = False

            # Check liquidation
            if position_type == 0 and low[i] <= liquidation_price:
                for idx in range(open_deals_log.shape[0]):
                    if not np.isnan(open_deals_log[idx, 0]):
                        completed_deals_log, pnl = log.close(
                            completed_deals_log,
                            commission,
                            open_deals_log[idx, 0],
                            open_deals_log[idx, 1],
                            700,
                            open_deals_log[idx, 2],
                            time[i],
                            open_deals_log[idx, 3],
                            liquidation_price,
                            open_deals_log[idx, 4],
                            initial_capital
                        )
                        equity += pnl

                open_deals_log = log.clear(open_deals_log)
                qty_entry[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                order_size = np.nan
                take_price[i] = np.nan
                entry_price_2[i] = np.nan
                entry_price_3[i] = np.nan
                entry_price_4[i] = np.nan
                alert_close_long = True

            # Long position management
            if position_type == 0:
                if close[i] <= open[i]:
                    if (
                        not np.isnan(take_price[i]) and
                        high[i] >= take_price[i]
                    ):
                        for idx in range(open_deals_log.shape[0]):
                            if not np.isnan(open_deals_log[idx, 0]):
                                completed_deals_log, pnl = log.close(
                                    completed_deals_log,
                                    commission,
                                    open_deals_log[idx, 0],
                                    open_deals_log[idx, 1],
                                    100,
                                    open_deals_log[idx, 2],
                                    time[i],
                                    open_deals_log[idx, 3],
                                    close[i],
                                    open_deals_log[idx, 4],
                                    initial_capital
                                )
                                equity += pnl

                        open_deals_log = log.clear(open_deals_log)
                        qty_entry[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[i] = np.nan
                        entry_price_2[i] = np.nan
                        entry_price_3[i] = np.nan
                        entry_price_4[i] = np.nan
                        alert_close_long = True

                if (
                    not np.isnan(entry_price_2[i]) and
                    low[i] <= entry_price_2[i]
                ):
                    order_signal = 301
                    order_price = entry_price_2[i]
                    order_date = time[i]

                    open_deals_log = log.open(
                        open_deals_log,
                        position_type,
                        order_signal,
                        order_date,
                        order_price,
                        qty_entry[1]
                    )

                    avg_entry_price = log.avg_price(open_deals_log)
                    if not np.isnan(avg_entry_price):
                        liquidation_price = adjust(
                            avg_entry_price * (1 - (1 / leverage)),
                            p_precision
                        )
                        take_price[i] = adjust(
                            avg_entry_price * (100 + take_profit) / 100,
                            p_precision
                        )

                    entry_price_2[i] = np.nan

                if (
                    not np.isnan(entry_price_3[i]) and
                    low[i] <= entry_price_3[i]
                ):
                    order_signal = 302
                    order_price = entry_price_3[i]
                    order_date = time[i]

                    open_deals_log = log.open(
                        open_deals_log,
                        position_type,
                        order_signal,
                        order_date,
                        order_price,
                        qty_entry[2]
                    )

                    avg_entry_price = log.avg_price(open_deals_log)
                    if not np.isnan(avg_entry_price):
                        liquidation_price = adjust(
                            avg_entry_price * (1 - (1 / leverage)),
                            p_precision
                        )
                        take_price[i] = adjust(
                            avg_entry_price * (100 + take_profit) / 100,
                            p_precision
                        )

                    entry_price_3[i] = np.nan

                if (
                    not np.isnan(entry_price_4[i]) and
                    low[i] <= entry_price_4[i]
                ):
                    order_signal = 303
                    order_price = entry_price_4[i]
                    order_date = time[i]

                    open_deals_log = log.open(
                        open_deals_log,
                        position_type,
                        order_signal,
                        order_date,
                        order_price,
                        qty_entry[3]
                    )

                    avg_entry_price = log.avg_price(open_deals_log)
                    if not np.isnan(avg_entry_price):
                        liquidation_price = adjust(
                            avg_entry_price * (1 - (1 / leverage)),
                            p_precision
                        )
                        take_price[i] = adjust(
                            avg_entry_price * (100 + take_profit) / 100,
                            p_precision
                        )

                    entry_price_4[i] = np.nan

                if close[i] > open[i]:
                    if (
                        not np.isnan(take_price[i]) and
                        high[i] >= take_price[i]
                    ):
                        for idx in range(open_deals_log.shape[0]):
                            if not np.isnan(open_deals_log[idx, 0]):
                                completed_deals_log, pnl = log.close(
                                    completed_deals_log,
                                    commission,
                                    open_deals_log[idx, 0],
                                    open_deals_log[idx, 1],
                                    100,
                                    open_deals_log[idx, 2],
                                    time[i],
                                    open_deals_log[idx, 3],
                                    close[i],
                                    open_deals_log[idx, 4],
                                    initial_capital
                                )
                                equity += pnl

                        open_deals_log = log.clear(open_deals_log)
                        qty_entry[:] = np.nan
                        position_type = np.nan
                        order_signal = np.nan
                        order_date = np.nan
                        order_price = np.nan
                        order_size = np.nan
                        take_price[i] = np.nan
                        entry_price_2[i] = np.nan
                        entry_price_3[i] = np.nan
                        entry_price_4[i] = np.nan
                        alert_close_long = True

            entry_long = (
                high[i] - low[i] >= sma[i] * mult and
                low[i] < lowest[i] and
                close[i] >= high[i] - (high[i] - low[i]) 
                    * range_threshold / 100 and
                np.isnan(order_size)  
            )

            if entry_long:
                position_type = 0
                order_signal = 100
                order_price = close[i]
                order_date = time[i]

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
                    
                liquidation_price = adjust(
                    order_price * (1 - (1 / leverage)), p_precision
                )
                entry_price_2[i] = adjust(
                    close[i] * (100 - entry_percent_2) / 100, p_precision
                )
                entry_price_3[i] = adjust(
                    entry_price_2[i] * (100 - entry_percent_3) / 100,
                    p_precision
                )
                entry_price_4[i] = adjust(
                    entry_price_3[i] * (100 - entry_percent_4) / 100,
                    p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 + take_profit) / 100, p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                qty_entry[0] = adjust(
                    order_size * entry_volumes[0] / 100, q_precision
                )
                qty_entry[1] = adjust(
                    order_size * entry_volumes[1] / 100, q_precision
                )
                qty_entry[2] = adjust(
                    order_size * entry_volumes[2] / 100, q_precision
                )
                qty_entry[3] = adjust(
                    order_size * entry_volumes[3] / 100, q_precision
                )

                if np.any(qty_entry == 0):
                    break

                open_deals_log = log.open(
                    open_deals_log,
                    position_type,
                    order_signal,
                    order_date,
                    order_price,
                    qty_entry[0]
                )

                alert_open_long = True

        return (
            completed_deals_log,
            open_deals_log,
            entry_price_2,
            entry_price_3,
            entry_price_4,
            take_price,
            alert_open_long,
            alert_close_long
        )
    
    def trade(self) -> None:
        if self.alert_close_long:
            self.client.trade.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )
            self.client.trade.cancel_all_orders(self.symbol)

        self.order_ids['limit_ids'] = self.client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_open_long:
            self.client.trade.cancel_all_orders(self.symbol)
            self.order_ids['limit_ids'] = (
                self.client.trade.check_limit_orders(
                    symbol=self.symbol,
                    order_ids=self.order_ids['limit_ids']
                )
            )

            self.client.trade.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size'] *
                       self.entry_volumes[0] / 100}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            order_id = self.client.trade.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size'] *
                       self.entry_volumes[1] / 100}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_2[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.trade.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size'] *
                       self.entry_volumes[2] / 100}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_3[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.trade.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['position_size'] *
                       self.entry_volumes[3] / 100}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_4[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)