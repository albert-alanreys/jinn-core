import numpy as np
import numba as nb

import src.core.quantklines as qk
import src.constants.colors as colors
from src.core.strategy.base_strategy import BaseStrategy
from src.core.strategy.deal_logger import update_completed_deals_log
from src.utils.rounding import adjust


class MeanStrikeV2(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes
    params = {
        "order_size_type": 0,
        "order_size": 50.0,
        "stop_loss": 1.0,
        "take_profit":  2.0,
        "grid_type": 1,
        "grid_size": 5,
        "first_grid_pct":  2.0,
        "grid_depth": 5.0,
        "martingale_coef": 2,
        "density_coef": 1.5,
        "lookback":  1,
        "ma_length":  20,
        "mult":  2.0,
        "range_threshold":  30.0
    }

    # Parameters to be optimized and their possible values
    opt_params = {
    }

    # Frontend rendering settings for indicators
    indicator_options = {
        'Stop-Loss': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON
        },
        'Take-Profit': {
            'pane': 0,
            'type': 'line',
            'color': colors.FOREST_GREEN
        },
        'Highest': {
            'pane': 0,
            'type': 'line',
            'lineWidth': 1,
            'color': colors.DARK_TURQUOISE
        },
        'Lowest': {
            'pane': 0,
            'type': 'line',
            'lineWidth': 1,
            'color': colors.DARK_ORCHID
        },
        'Price Range': {
            'pane': 1,
            'type': 'line',
            'color': colors.DEEP_SKY_BLUE
        },
        'SMA Threshold': {
            'pane': 1,
            'type': 'line',
            'color': colors.ORANGE
        },

    }

    def __init__(self, client, all_params = None, opt_params = None) -> None:
        super().__init__(client, all_params, opt_params)

    def calculate(self, market_data) -> None:
        super().init_variables(market_data, self.params['grid_size'] + 1)

        self.grid_prices = np.full(
            (self.params['grid_size'], self.time.shape[0]), np.nan
        )
        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.full(self.time.shape[0], np.nan)

        self.liquidation_price = np.nan
        self.order_quantities = np.full(self.params['grid_size'] + 1, np.nan)

        self.lowest = qk.lowest(
            source=np.roll(self.low, 1),
            length=self.params['lookback']
        )
        self.highest = qk.highest(
            source=np.roll(self.high, 1),
            length=self.params['lookback']
        )
        self.price_range = self.high - self.low
        self.sma = qk.sma(
            source=self.price_range, 
            length=self.params['ma_length']
        )
        self.sma_threshold = self.sma * self.params['mult']

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
            self.params['order_size_type'],
            self.params['order_size'],
            self.params['leverage'],
            self.params['stop_loss'],
            self.params['take_profit'],
            self.params['grid_type'],
            self.params['grid_size'],
            self.params['first_grid_pct'],
            self.params['grid_depth'],
            self.params['martingale_coef'],
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
            self.entry_signal,
            self.entry_price,
            self.entry_date,
            self.deal_type,
            self.grid_prices,
            self.stop_price,
            self.take_price,
            self.liquidation_price,
            self.order_quantities,
            self.lowest,
            self.highest,
            self.price_range,
            self.sma_threshold,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_open_short,
            self.alert_close_long,
            self.alert_close_short
        )

        self.indicators = {
            'Stop-Loss': {
                'options': self.indicator_options['Stop-Loss'],
                'values': self.stop_price
            },
            'Take-Profit': {
                'options': self.indicator_options['Take-Profit'],
                'values': self.take_price
            },
            'Highest': {
                'options': self.indicator_options['Highest'],
                'values': self.highest
            },
            'Lowest': {
                'options': self.indicator_options['Lowest'],
                'values': self.lowest
            },
            'Price Range': {
                'options': self.indicator_options['Price Range'],
                'values': self.price_range
            },
            'SMA Threshold': {
                'options': self.indicator_options['SMA Threshold'],
                'values': self.sma_threshold
            },
        }

    @staticmethod
    # @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        direction: int,
        initial_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        stop_loss: float,
        take_profit: float,
        grid_type: int,
        grid_size: int,
        first_grid_pct: float,
        grid_depth: float,
        martingale_coef: float,
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
        entry_signal: float,
        entry_price: float,
        entry_date: float,
        deal_type: float,
        grid_prices: np.ndarray,
        stop_price: np.ndarray,
        take_price: np.ndarray,
        liquidation_price: float,
        order_quantities: np.ndarray,
        lowest: np.ndarray,
        highest: np.ndarray,
        price_range: np.ndarray,
        sma_threshold: np.ndarray,
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
                    deal_type == 0
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_long = True

                if deal_type == 0:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            low[i] <= grid_price
                        ):
                            entry_signal = 300 + order_idx
                            entry_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                deal_type, entry_signal, entry_date,
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
                    deal_type == 0
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (low[i] <= liquidation_price and deal_type == 0):
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True
            else:
                if deal_type == 0:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            low[i] <= grid_price
                        ):
                            entry_signal = 300 + order_idx
                            entry_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                deal_type, entry_signal, entry_date,
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
                    deal_type == 0
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (low[i] <= liquidation_price and deal_type == 0):
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_price[i]) and
                    high[i] >= take_price[i] and
                    deal_type == 0
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
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
                deal_type = 0
                entry_signal = 100
                entry_price = close[i]
                entry_date = time[i]

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
                if order_size_type == 0:
                    initial_position =  (
                        equity * leverage * (order_size / 100.0)
                    )
                elif order_size_type == 1:
                    initial_position = order_size * leverage

                sum_k = sum(
                    [martingale_coef ** n for n in range(grid_size + 1)]
                )
                first_order_value = initial_position / sum_k

                for n in range(grid_size + 1):
                    order_capital = first_order_value * (martingale_coef ** n)

                    if n == 0:
                        price = entry_price
                    else:
                        price = grid_prices[n - 1, i]

                    quantity = order_capital * (1 - commission / 100) / price
                    order_quantities[n] = adjust(quantity, q_precision)

                liquidation_price = adjust(
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    grid_prices[-1, i] * (100 - stop_loss) / 100, p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 + take_profit) / 100, p_precision
                )
                open_deals_log[0] = np.array([
                    deal_type, entry_signal, entry_date,
                    entry_price, order_quantities[0]
                ])
                alert_open_long = True

            # Trading logic (shorts)
            if close[i] >= open[i]:
                if (
                    not np.isnan(take_price[i]) and
                    low[i] <= take_price[i] and
                    deal_type == 1
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_close_short = True

                if deal_type == 1:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            high[i] >= grid_price
                        ):
                            entry_signal = 400 + order_idx
                            entry_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                deal_type, entry_signal, entry_date,
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
                    deal_type == 1
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                if (high[i] >= liquidation_price and deal_type == 1):
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True
            else:
                if deal_type == 1:
                    for order_idx in range(1, grid_size + 1):
                        grid_price = grid_prices[order_idx - 1, i]

                        if (
                            not np.isnan(grid_price) and
                            high[i] >= grid_price
                        ):
                            entry_signal = 400 + order_idx
                            entry_date = time[i]

                            open_deals_log[order_idx] = np.array([
                                deal_type, entry_signal, entry_date,
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
                    deal_type == 1
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan

                if (high[i] >= liquidation_price and deal_type == 1):
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
                    grid_prices[:, i] = np.nan
                    stop_price[i] = np.nan
                    take_price[i] = np.nan
                    alert_cancel = True

                if (
                    not np.isnan(take_price[i]) and
                    low[i] <= take_price[i] and
                    deal_type == 1
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
                    deal_type = np.nan
                    entry_signal = np.nan
                    entry_date = np.nan
                    entry_price = np.nan
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
                deal_type = 1
                entry_signal = 200
                entry_price = close[i]
                entry_date = time[i]

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
                if order_size_type == 0:
                    initial_position =  (
                        equity * leverage * (order_size / 100.0)
                    )
                elif order_size_type == 1:
                    initial_position = order_size * leverage

                sum_k = sum(
                    [martingale_coef ** n for n in range(grid_size + 1)]
                )
                first_order_value = initial_position / sum_k

                for n in range(grid_size + 1):
                    order_capital = first_order_value * (martingale_coef ** n)

                    if n == 0:
                        price = entry_price
                    else:
                        price = grid_prices[n - 1, i]

                    quantity = order_capital * (1 - commission / 100) / price
                    order_quantities[n] = adjust(quantity, q_precision)

                liquidation_price = adjust(
                    entry_price * (1 + (1 / leverage)), p_precision
                )
                stop_price[i] = adjust(
                    grid_prices[-1, i] * (100 + stop_loss) / 100, p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 - take_profit) / 100, p_precision
                )
                open_deals_log[0] = np.array([
                    deal_type, entry_signal, entry_date,
                    entry_price, order_quantities[0]
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
    
    def trade(self) -> None:
        if self.order_ids is None:
            self.order_ids = self.cache.load(self.symbol)

        self.cache.save(self.symbol, self.order_ids)