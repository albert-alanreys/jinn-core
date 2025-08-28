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


class MeanStrikeV2(BaseStrategy):
    # --- Strategy Configuration ---
    # Default parameter values for backtesting and live trading
    params = {
        'direction': 0,
        'leverage': 1,
        'position_size_type': 0,
        'position_size': 10.0,
        'first_order_pct': 10.0,
        'stop_loss': 1.0,
        'take_profit': 2.0,
        'grid_type': 1,
        'grid_size': 4,
        'first_grid_pct': 2.0,
        'grid_depth': 5.0,
        'martingale_coef': 0.0,
        'density_coef': 1.5,
        'lookback': 1,
        'ma_length': 20,
        'mult': 2.0,
        'range_threshold': 30.0,
    }

    # --- Optimization Space ---
    # Parameter ranges for hyperparameter optimization
    opt_params = {
        'stop_loss': [i / 10 for i in range(2, 101, 2)],
        'take_profit': [i / 10 for i in range(2, 101, 2)],
        'grid_type': [0, 1],
        'grid_size': [i for i in range(2, 21)],
        'first_grid_pct': [i / 10 for i in range(4, 51, 2)],
        'grid_depth': [float(i) for i in range(1, 51)],
        'density_coef': [i / 10 for i in range(5, 16)],
        'lookback': [i for i in range(1, 21)],
        'ma_length': [i for i in range(10, 101)],
        'mult': [i / 10 for i in range(10, 31)],
        'range_threshold': [float(i) for i in range(10, 100)],
    }

    # --- UI/UX Configuration ---
    # Human-readable labels for frontend parameter display
    param_labels = {
        'direction': 'Trade Direction',
        'leverage': 'Leverage',
        'position_size_type': 'Position Size Type',
        'position_size': 'Position Size',
        'first_order_pct': 'First Order (%)',
        'stop_loss': 'Stop Loss (%)',
        'take_profit': 'Take Profit (%)',
        'grid_type': 'Grid Type',
        'grid_size': 'Grid Levels',
        'first_grid_pct': 'First Grid (%)',
        'grid_depth': 'Grid Depth (%)',
        'martingale_coef': 'Martingale Coef',
        'density_coef': 'Density Coef',
        'lookback': 'Lookback Bars',
        'ma_length': 'MA Length',
        'mult': 'Multiplier',
        'range_threshold': 'Range Threshold',
    }

    # --- Visualization Settings ---
    # Chart styling configuration for technical indicators
    indicator_options = {
        'Stop-Loss': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON,
        },
        'Take-Profit': {
            'pane': 0,
            'type': 'line',
            'color': colors.FOREST_GREEN,
        },
        'Highest': {
            'pane': 0,
            'type': 'line',
            'lineWidth': 1,
            'color': colors.DARK_TURQUOISE,
        },
        'Lowest': {
            'pane': 0,
            'type': 'line',
            'lineWidth': 1,
            'color': colors.DARK_ORCHID,
        },
        'Price Range': {
            'pane': 1,
            'type': 'line',
            'color': colors.DEEP_SKY_BLUE,
        },
        'SMA Threshold': {
            'pane': 1,
            'type': 'line',
            'color': colors.ORANGE,
        },
    }

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)

    def calculate(self, market_data) -> None:
        super().init_variables(market_data, self.params['grid_size'] + 1)

        self.grid_prices = np.full(
            (self.params['grid_size'], self.time.shape[0]), np.nan
        )
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.full(self.time.shape[0], np.nan)

        self.liquidation_price = np.nan
        self.order_quantities = np.full(self.params['grid_size'] + 1, np.nan)

        self.lowest = quantklines.lowest(
            source=np.roll(self.low, 1),
            length=self.params['lookback']
        )
        self.highest = quantklines.highest(
            source=np.roll(self.high, 1),
            length=self.params['lookback']
        )
        self.price_range = self.high - self.low
        self.sma = quantklines.sma(
            source=self.price_range, 
            length=self.params['ma_length']
        )
        self.sma_threshold = self.sma * self.params['mult']

        if self.params['martingale_coef'] == 0.0:
            self.martingale_coef = self._get_optimal_martingale_coef(
                self.params['first_order_pct'],
                self.params['grid_size']
            )
        else:
            self.martingale_coef = self.params['martingale_coef']

        self.order_values = np.full(self.params['grid_size'] + 1, np.nan)

        first_order_value =  (
            self.params['first_order_pct'] *
            self.params['position_size'] / 100
        )

        for n in range(self.order_values.shape[0]):
            order_value = (
                first_order_value * (self.martingale_coef ** n)
            )
            self.order_values[n] = order_value

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_open_short = False
        self.alert_close_long = False
        self.alert_close_short = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.grid_prices,
            self.stop_price,
            self.take_price,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short
        ) = self._calculate_loop(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['commission'],
            self.params['position_size_type'],
            self.params['position_size'],
            self.params['leverage'],
            self.params['stop_loss'],
            self.params['take_profit'],
            self.params['grid_type'],
            self.params['grid_size'],
            self.params['first_grid_pct'],
            self.params['grid_depth'],
            self.params['density_coef'],
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
            self.position_type,
            self.grid_prices,
            self.stop_price,
            self.take_price,
            self.liquidation_price,
            self.order_quantities,
            self.lowest,
            self.highest,
            self.price_range,
            self.sma_threshold,
            self.martingale_coef,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short
        )

        self.indicators = {
            'Stop-Loss': {
                'options': self.indicator_options['Stop-Loss'],
                'values': self.stop_price,
            },
            'Take-Profit': {
                'options': self.indicator_options['Take-Profit'],
                'values': self.take_price,
            },
            'Highest': {
                'options': self.indicator_options['Highest'],
                'values': self.highest,
            },
            'Lowest': {
                'options': self.indicator_options['Lowest'],
                'values': self.lowest,
            },
            'Price Range': {
                'options': self.indicator_options['Price Range'],
                'values': self.price_range,
            },
            'SMA Threshold': {
                'options': self.indicator_options['SMA Threshold'],
                'values': self.sma_threshold,
            },
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _get_optimal_martingale_coef(
        first_order_pct: float,
        grid_size: int,
    ) -> float:
        def equation(k, grid_size, target_sum_progression):
            if abs(k - 1.0) < 1e-10:
                return (grid_size + 1) - target_sum_progression
            
            return (1 - k**(grid_size + 1)) / (1 - k) - target_sum_progression
        
        target_first_order_ratio = first_order_pct / 100.0
        target_sum_progression = 1.0 / target_first_order_ratio
        
        if abs(target_sum_progression - (grid_size + 1)) < 1e-6:
            return 1.0
        
        left, right = 0.1, 5.0
        left_val = equation(left, grid_size, target_sum_progression)
        right_val = equation(right, grid_size, target_sum_progression)

        if left_val * right_val > 0:
            return 1.0
        
        for _ in range(50):
            mid = (left + right) / 2.0
            mid_val = equation(mid, grid_size, target_sum_progression)

            if abs(mid_val) < 1e-8:
                break

            left_val = equation(left, grid_size, target_sum_progression)
            if left_val * mid_val < 0:
                right = mid
            else:
                left = mid
        
        optimal_k = (left + right) / 2.0

        if optimal_k <= 0 or optimal_k > 10:
            return 1.0
        
        return optimal_k

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        direction: int,
        initial_capital: float,
        commission: float,
        position_size_type: int,
        position_size: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
        grid_type: int,
        grid_size: int,
        first_grid_pct: float,
        grid_depth: float,
        density_coef: float,
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
        position_type: float,
        grid_prices: np.ndarray,
        stop_price: np.ndarray,
        take_price: np.ndarray,
        liquidation_price: float,
        order_quantities: np.ndarray,
        lowest: np.ndarray,
        highest: np.ndarray,
        price_range: np.ndarray,
        sma_threshold: np.ndarray,
        martingale_coef: float,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_open_short: bool,
        alert_close_long: bool,
        alert_close_short: bool
    ) -> tuple:
        for i in range(1, time.shape[0]):
            grid_prices[:, i] = grid_prices[:, i - 1]
            stop_price[i] = stop_price[i - 1]
            take_price[i] = take_price[i - 1]

            alert_cancel = False
            alert_open_long = False
            alert_open_short = False
            alert_close_long = False
            alert_close_short = False

            # Trading logic (longs)
            if close[i] <= open[i]:
                if (
                    not np.isnan(take_price[i]) and
                    high[i] >= take_price[i] and
                    position_type == 0
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                100,
                                deal[2],
                                time[i],
                                deal[3],
                                close[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_long = True

                if position_type == 0:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            low[i] <= grid_price
                        ):
                            order_signal = 300 + order_idx
                            order_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                position_type, order_signal, order_date,
                                grid_price, order_quantities[order_idx]
                            ])

                            valid_deals = ~np.isnan(open_deals_log[:, 0])
                            avg_entry_price = np.nansum(
                                open_deals_log[valid_deals, 3] *
                                open_deals_log[valid_deals, 4]
                            ) / np.nansum(open_deals_log[valid_deals, 4])
                            
                            liquidation_price = adjust(
                                avg_entry_price * (1 - (1 / leverage)),
                                p_precision
                            )
                            take_price[i] = adjust(
                                avg_entry_price * (100 + take_profit) / 100,
                                p_precision
                            )
                            grid_prices[order_idx - 1, i] = np.nan

                if (
                    not np.isnan(stop_price[i]) and
                    low[i] <= stop_price[i] and
                    position_type == 0
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                500,
                                deal[2],
                                time[i],
                                deal[3],
                                stop_price[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (low[i] <= liquidation_price and position_type == 0):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                700,
                                deal[2],
                                time[i],
                                deal[3],
                                liquidation_price,
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True
            else:
                if position_type == 0:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            low[i] <= grid_price
                        ):
                            order_signal = 300 + order_idx
                            order_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                position_type, order_signal, order_date,
                                grid_price, order_quantities[order_idx]
                            ])

                            valid_deals = ~np.isnan(open_deals_log[:, 0])
                            avg_entry_price = np.nansum(
                                open_deals_log[valid_deals, 3] *
                                open_deals_log[valid_deals, 4]
                            ) / np.nansum(open_deals_log[valid_deals, 4])
                            
                            liquidation_price = adjust(
                                avg_entry_price * (1 - (1 / leverage)),
                                p_precision
                            )
                            take_price[i] = adjust(
                                avg_entry_price * (100 + take_profit) / 100,
                                p_precision
                            )
                            grid_prices[order_idx - 1, i] = np.nan

                if (
                    not np.isnan(stop_price[i]) and
                    low[i] <= stop_price[i] and
                    position_type == 0
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                500,
                                deal[2],
                                time[i],
                                deal[3],
                                stop_price[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (low[i] <= liquidation_price and position_type == 0):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                700,
                                deal[2],
                                time[i],
                                deal[3],
                                liquidation_price,
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_price[i]) and
                    high[i] >= take_price[i] and
                    position_type == 0
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                100,
                                deal[2],
                                time[i],
                                deal[3],
                                close[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_long = True

            entry_long = (
                np.isnan(order_quantities).all() and
                price_range[i] >= sma_threshold[i] and
                low[i] < lowest[i] and
                close[i] >= high[i] - (
                    price_range[i] * range_threshold / 100
                ) and (direction == 0 or direction == 1)
            )

            if entry_long:
                position_type = 0
                order_signal = 100
                order_price = close[i]
                order_date = time[i]

                # grid calculation
                first_grid_price = close[i] * (100 - first_grid_pct) / 100

                if grid_type == 0:
                    for n in range(grid_size):
                        if n == 0:
                            price = first_grid_price
                        else:
                            price = first_grid_price * (
                                1 - grid_depth / 100 * n / (grid_size - 1)
                            )

                        grid_prices[n, i] = adjust(price, p_precision)
                elif grid_type == 1:
                    for n in range(grid_size):
                        if n == 0:
                            price = first_grid_price
                        else:
                            progress = n / (grid_size - 1)
                            log_progress = progress ** (density_coef)
                            depth_pct = log_progress * grid_depth / 100
                            price = first_grid_price * (1 - depth_pct)

                        grid_prices[n, i] = adjust(price, p_precision)

                # calculation of quantities
                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                else:
                    initial_position = position_size * leverage

                sum_k = sum([
                    martingale_coef ** n
                    for n in range(grid_size + 1)
                ])
                first_order_value = initial_position / sum_k

                for n in range(grid_size + 1):
                    order_value = (
                        first_order_value * (martingale_coef ** n)
                    )

                    if n == 0:
                        price = order_price
                    else:
                        price = grid_prices[n - 1, i]

                    quantity = order_value * (1 - commission / 100) / price
                    order_quantities[n] = adjust(quantity, q_precision)

                if np.any(order_quantities <= 0):
                    position_type = np.nan
                    order_signal = np.nan
                    order_price = np.nan
                    order_date = np.nan
                    continue

                liquidation_price = adjust(
                    order_price * (1 - (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    grid_prices[-1, i] * (100 - stop_loss) / 100, p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 + take_profit) / 100, p_precision
                )
                open_deals_log[0] = np.array([
                    position_type, order_signal, order_date,
                    order_price, order_quantities[0]
                ])
                alert_open_long = True

            # Trading logic (shorts)
            if close[i] >= open[i]:
                if (
                    not np.isnan(take_price[i]) and
                    low[i] <= take_price[i] and
                    position_type == 1
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                200,
                                deal[2],
                                time[i],
                                deal[3],
                                close[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_short = True

                if position_type == 1:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            high[i] >= grid_price
                        ):
                            order_signal = 400 + order_idx
                            order_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                position_type, order_signal, order_date,
                                grid_price, order_quantities[order_idx]
                            ])

                            valid_deals = ~np.isnan(open_deals_log[:, 0])
                            avg_entry_price = np.nansum(
                                open_deals_log[valid_deals, 3] *
                                open_deals_log[valid_deals, 4]
                            ) / np.nansum(open_deals_log[valid_deals, 4])
                            
                            liquidation_price = adjust(
                                avg_entry_price * (1 + (1 / leverage)),
                                p_precision
                            )
                            take_price[i] = adjust(
                                avg_entry_price * (100 - take_profit) / 100,
                                p_precision
                            )
                            grid_prices[order_idx - 1, i] = np.nan

                if (
                    not np.isnan(stop_price[i]) and
                    high[i] >= stop_price[i] and
                    position_type == 1
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                600,
                                deal[2],
                                time[i],
                                deal[3],
                                stop_price[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                if (high[i] >= liquidation_price and position_type == 1):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                800,
                                deal[2],
                                time[i],
                                deal[3],
                                liquidation_price,
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True
            else:
                if position_type == 1:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            high[i] >= grid_price
                        ):
                            order_signal = 400 + order_idx
                            order_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                position_type, order_signal, order_date,
                                grid_price, order_quantities[order_idx]
                            ])

                            valid_deals = ~np.isnan(open_deals_log[:, 0])
                            avg_entry_price = np.nansum(
                                open_deals_log[valid_deals, 3] *
                                open_deals_log[valid_deals, 4]
                            ) / np.nansum(open_deals_log[valid_deals, 4])
                            
                            liquidation_price = adjust(
                                avg_entry_price * (1 + (1 / leverage)),
                                p_precision
                            )
                            take_price[i] = adjust(
                                avg_entry_price * (100 - take_profit) / 100,
                                p_precision
                            )
                            grid_prices[order_idx - 1, i] = np.nan
                if (
                    not np.isnan(stop_price[i]) and
                    high[i] >= stop_price[i] and
                    position_type == 1
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                600,
                                deal[2],
                                time[i],
                                deal[3],
                                stop_price[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (high[i] >= liquidation_price and position_type == 1):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                800,
                                deal[2],
                                time[i],
                                deal[3],
                                liquidation_price,
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_price[i]) and
                    low[i] <= take_price[i] and
                    position_type == 1
                ):
                    for deal in open_deals_log:
                        if not np.isnan(deal[0]):
                            (
                                completed_deals_log,
                                pnl,
                            ) = update_completed_deals_log(
                                completed_deals_log,
                                commission,
                                deal[0],
                                deal[1],
                                200,
                                deal[2],
                                time[i],
                                deal[3],
                                close[i],
                                deal[4],
                                initial_capital
                            )
                            equity += pnl

                    open_deals_log[:] = np.nan
                    order_quantities[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_short = True

            entry_short = (
                np.isnan(order_quantities).all() and
                price_range[i] >= sma_threshold[i] and
                high[i] > highest[i] and
                close[i] <= low[i] + (
                    price_range[i] * range_threshold / 100
                ) and (direction == 0 or direction == 2)
            )

            if entry_short:
                position_type = 1
                order_signal = 200
                order_price = close[i]
                order_date = time[i]

                # grid calculation
                first_grid_price = close[i] * (100 + first_grid_pct) / 100

                if grid_type == 0:
                    for n in range(grid_size):
                        if n == 0:
                            price = first_grid_price
                        else:
                            price = first_grid_price * (
                                1 + grid_depth / 100 * n / (grid_size - 1)
                            )

                        grid_prices[n, i] = adjust(price, p_precision)
                elif grid_type == 1:
                    for n in range(grid_size):
                        if n == 0:
                            price = first_grid_price
                        else:
                            progress = n / (grid_size - 1)
                            log_progress = progress ** (density_coef)
                            depth_pct = log_progress * grid_depth / 100
                            price = first_grid_price * (1 + depth_pct)

                        grid_prices[n, i] = adjust(price, p_precision)

                # calculation of quantities
                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                else:
                    initial_position = position_size * leverage

                sum_k = sum([
                    martingale_coef ** n
                    for n in range(grid_size + 1)
                ])
                first_order_value = initial_position / sum_k

                for n in range(grid_size + 1):
                    order_value = (
                        first_order_value * (martingale_coef ** n)
                    )

                    if n == 0:
                        price = order_price
                    else:
                        price = grid_prices[n - 1, i]

                    quantity = order_value * (1 - commission / 100) / price
                    order_quantities[n] = adjust(quantity, q_precision)

                if np.any(order_quantities <= 0):
                    position_type = np.nan
                    order_signal = np.nan
                    order_price = np.nan
                    order_date = np.nan
                    continue

                liquidation_price = adjust(
                    order_price * (1 + (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    grid_prices[-1, i] * (100 + stop_loss) / 100, p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 - take_profit) / 100, p_precision
                )
                open_deals_log[0] = np.array([
                    position_type, order_signal, order_date,
                    order_price, order_quantities[0]
                ])
                alert_open_short = True

        return (
            completed_deals_log,
            open_deals_log,
            grid_prices,
            stop_price,
            take_price,
            alert_cancel,
            alert_open_long,
            alert_open_short,
            alert_close_long,
            alert_close_short
        )

    def _trade(self, client: BaseExchangeClient) -> None:
        # General
        if self.alert_cancel:
            client.trade.cancel_all_orders(self.symbol)

        # Longs
        if self.alert_close_long:
            client.trade.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )
            client.trade.cancel_all_orders(self.symbol)

        if self.alert_open_long:
            client.trade.cancel_all_orders(self.symbol)

            client.trade.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.order_values[0]}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            for i in range(self.params['grid_size']):
                order_id = client.trade.limit_open_long(
                    symbol=self.symbol,
                    size=(
                        f'{self.order_values[i + 1]}'
                        f'{'u' if self.params['position_size_type'] else '%'}'
                    ),
                    margin=(
                        'cross' if self.params['margin_type'] else 'isolated'
                    ),
                    leverage=self.params['leverage'],
                    price=self.grid_prices[i, -1],
                    hedge=False
                )

                if order_id:
                    self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.market_stop_close_long(
                symbol=self.symbol,
                size='100%',
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

        # Shorts
        if self.alert_close_short:
            client.trade.market_close_short(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )
            client.trade.cancel_all_orders(self.symbol)

        if self.alert_open_short:
            client.trade.cancel_all_orders(self.symbol)

            client.trade.market_open_short(
                symbol=self.symbol,
                size=(
                    f'{self.order_values[0]}'
                    f'{'u' if self.params['position_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            for i in range(self.params['grid_size']):
                order_id = client.trade.limit_open_short(
                    symbol=self.symbol,
                    size=(
                        f'{self.order_values[i + 1]}'
                        f'{'u' if self.params['position_size_type'] else '%'}'
                    ),
                    margin=(
                        'cross' if self.params['margin_type'] else 'isolated'
                    ),
                    leverage=self.params['leverage'],
                    price=self.grid_prices[i, -1],
                    hedge=False
                )

                if order_id:
                    self.order_ids['limit_ids'].append(order_id)

            order_id = client.trade.market_stop_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.stop_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

        # Order Monitoring
        self.order_ids['limit_ids'] = client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        self.order_ids['stop_ids'] = client.trade.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )