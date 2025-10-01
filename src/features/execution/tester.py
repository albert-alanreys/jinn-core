from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import numba as nb

if TYPE_CHECKING:
    from src.core.providers import MarketData
    from src.core.strategies import BaseStrategy
    from .models import Metric, OverviewMetrics, StrategyMetrics


class StrategyTester:
    """
    Comprehensive strategy performance testing and metrics calculation.
    
    Processes trading deal logs to generate detailed performance
    analytics across four key categories: overview,
    performance, trades, and risk metrics.
    """

    def test(
        self,
        strategy: BaseStrategy,
        market_data: MarketData
    ) -> StrategyMetrics:
        """
        Run full strategy backtest and compute metrics.
        
        Args:
            strategy: Strategy instance to evaluate
            market_data: Market data package

        Returns:
            StrategyMetrics: Complete performance metrics set
        """

        if market_data['klines'].size == 0:
            return self._get_empty_metrics_structure()

        strategy.__calculate__(market_data)

        all_metrics = self._calculate_all_metrics(
            initial_capital=strategy.params['initial_capital'],
            deals_log=strategy.completed_deals_log
        )

        return {
            'overview': self._extract_overview_metrics(all_metrics),
            'performance': self._extract_performance_metrics(all_metrics),
            'trades': self._extract_trade_metrics(all_metrics),
            'risk': self._extract_risk_metrics(all_metrics),
        }

    def _extract_overview_metrics(
        self,
        all_metrics: dict[str, np.ndarray | Metric]
    ) -> OverviewMetrics:
        """
        Extract high-level overview metrics for strategy summary.

        Args:
            all_metrics: Complete calculated metrics dictionary

        Returns:
            OverviewMetrics:
                Overview metrics with primary indicators and equity curve
        """

        return {
            'primary': [
                all_metrics['Net Profit'],
                all_metrics['Profit Factor'],
                all_metrics['Max Equity Drawdown'],
                all_metrics['Average per Trade'],
                all_metrics['Number of Winning Trades'],
                all_metrics['Total Closed Trades'],
            ],
            'equity': all_metrics['equity'],
        }

    def _extract_performance_metrics(
        self,
        all_metrics: dict[str, np.ndarray | Metric]
    ) -> list[Metric]:
        """
        Extract performance-related metrics.
        
        Args:
            all_metrics: Complete calculated metrics dictionary
            
        Returns:
            List of performance metrics
        """

        return [
            all_metrics['Net Profit'],
            all_metrics['Profit Factor'],
            all_metrics['Recovery Factor'],
            all_metrics['Max Equity Run-Up'],
            all_metrics['Max Order Size'],
            all_metrics['Gross Profit'],
            all_metrics['Gross Loss'],
            all_metrics['Commission Paid'],
        ]

    def _extract_trade_metrics(
        self,
        all_metrics: dict[str, np.ndarray | Metric]
    ) -> list[Metric]:
        """
        Extract trade execution and quality metrics.
        
        Args:
            all_metrics: Complete calculated metrics dictionary
            
        Returns:
            List of trade-related metrics
        """

        return [
            all_metrics['Total Closed Trades'],
            all_metrics['Number of Winning Trades'],
            all_metrics['Number of Losing Trades'],
            all_metrics['Winning Trade Percentage'],
            all_metrics['Average per Trade'],
            all_metrics['Average Profit per Trade'],
            all_metrics['Average Loss per Trade'],
            all_metrics['Average Win / Average Loss Ratio'],
            all_metrics['Largest Winning Trade'],
            all_metrics['Largest Losing Trade'],
        ]

    def _extract_risk_metrics(
        self,
        all_metrics: dict[str, np.ndarray | Metric]
    ) -> list[Metric]:
        """
        Extract risk management and volatility metrics.
        
        Args:
            all_metrics: Complete calculated metrics dictionary
            
        Returns:
            List of risk-adjusted metrics
        """

        return [
            all_metrics['Max Equity Drawdown'],
            all_metrics['Sharpe Ratio'],
            all_metrics['Sortino Ratio'],
            all_metrics['Skewness'],
            all_metrics['Number of Liquidations'],
        ]

    def _calculate_all_metrics(
        self,
        initial_capital: float,
        deals_log: np.ndarray
    ) -> dict[str, np.ndarray | Metric]:
        """
        Calculate comprehensive strategy metrics from deal logs.

        Expected deals_log structure:
        - Column 0: Trade direction (0=long, 1=short)
        - Column 2: Exit signal code
        - Column 7: Position size in units
        - Column 8: Trade P&L in currency
        - Column 9: Trade P&L in percentage
        - Column 12: Commission paid

        Args:
            initial_capital: Starting capital amount
            deals_log: Array of completed trades with structured columns

        Returns:
            dict: Complete metrics dictionary with categorized data
        """

        def _fmt2(x):
            return np.round(x, 2) if not np.isnan(x) else np.nan
        
        def _fmt3(x):
            return np.round(x, 3) if not np.isnan(x) else np.nan
        
        # Calculate all metrics using numba-optimized function
        metrics_data = self._calculate_metrics(
            initial_capital, deals_log
        )
        
        # Unpack the results tuple
        (
            equity,

            # Gross Profit data
            all_gross_profit,
            all_gross_profit_pct,
            long_gross_profit,
            long_gross_profit_pct,
            short_gross_profit,
            short_gross_profit_pct,

            # Gross Loss data
            all_gross_loss,
            all_gross_loss_pct,
            long_gross_loss,
            long_gross_loss_pct,
            short_gross_loss,
            short_gross_loss_pct,

            # Net Profit data
            all_net_profit,
            all_net_profit_pct,
            long_net_profit,
            long_net_profit_pct,
            short_net_profit,
            short_net_profit_pct,

            # Profit Factor data
            all_profit_factor,
            long_profit_factor,
            short_profit_factor,

            # Commission data
            all_commission_paid,
            long_commission_paid,
            short_commission_paid,

            # Max Order Size data
            all_max_order_size,
            long_max_order_size,
            short_max_order_size,

            # Trade counts
            all_total_closed_trades,
            long_total_closed_trades,
            short_total_closed_trades,
            all_number_winning_trades,
            long_number_winning_trades,
            short_number_winning_trades,
            all_number_losing_trades,
            long_number_losing_trades,
            short_number_losing_trades,

            # Percentages and averages
            all_percent_profitable,
            long_percent_profitable,
            short_percent_profitable,
            all_avg_trade,
            all_avg_trade_pct,
            long_avg_trade,
            long_avg_trade_pct,
            short_avg_trade,
            short_avg_trade_pct,
            all_avg_winning_trade,
            all_avg_winning_trade_pct,
            long_avg_winning_trade,
            long_avg_winning_trade_pct,
            short_avg_winning_trade,
            short_avg_winning_trade_pct,
            all_avg_losing_trade,
            all_avg_losing_trade_pct,
            long_avg_losing_trade,
            long_avg_losing_trade_pct,
            short_avg_losing_trade,
            short_avg_losing_trade_pct,

            # Ratios
            all_ratio_avg_win_loss,
            long_ratio_avg_win_loss,
            short_ratio_avg_win_loss,

            # Largest trades
            all_largest_winning_trade,
            all_largest_winning_trade_pct,
            long_largest_winning_trade,
            long_largest_winning_trade_pct,
            short_largest_winning_trade,
            short_largest_winning_trade_pct,
            all_largest_losing_trade,
            all_largest_losing_trade_pct,
            long_largest_losing_trade,
            long_largest_losing_trade_pct,
            short_largest_losing_trade,
            short_largest_losing_trade_pct,

            # Risk metrics
            all_max_runup,
            all_max_runup_pct,
            all_max_drawdown,
            all_max_drawdown_pct,
            all_recovery_factor,
            all_sharpe_ratio,
            all_sortino_ratio,
            all_skew,

            # Liquidations
            all_liquidations_number,
            long_liquidations_number,
            short_liquidations_number
        ) = metrics_data

        # Aggregate metrics into structured dictionary
        return {
            'equity': equity,
            'Gross Profit': {
                'title': 'Gross Profit',
                'all': [
                    _fmt2(all_gross_profit),
                    _fmt2(all_gross_profit_pct)
                ],
                'long': [
                    _fmt2(long_gross_profit),
                    _fmt2(long_gross_profit_pct)
                ],
                'short': [
                    _fmt2(short_gross_profit),
                    _fmt2(short_gross_profit_pct)
                ]
            },
            'Gross Loss': {
                'title': 'Gross Loss',
                'all': [
                    _fmt2(all_gross_loss),
                    _fmt2(all_gross_loss_pct)
                ],
                'long': [
                    _fmt2(long_gross_loss),
                    _fmt2(long_gross_loss_pct)
                ],
                'short': [
                    _fmt2(short_gross_loss),
                    _fmt2(short_gross_loss_pct)
                ]
            },
            'Net Profit': {
                'title': 'Net Profit',
                'all': [
                    _fmt2(all_net_profit),
                    _fmt2(all_net_profit_pct)
                ],
                'long': [
                    _fmt2(long_net_profit),
                    _fmt2(long_net_profit_pct)
                ],
                'short': [
                    _fmt2(short_net_profit),
                    _fmt2(short_net_profit_pct)
                ]
            },
            'Profit Factor': {
                'title': 'Profit Factor',
                'all': [_fmt3(all_profit_factor)],
                'long': [_fmt3(long_profit_factor)],
                'short': [_fmt3(short_profit_factor)]
            },
            'Commission Paid': {
                'title': 'Commission Paid',
                'all': [_fmt2(all_commission_paid)],
                'long': [_fmt2(long_commission_paid)],
                'short': [_fmt2(short_commission_paid)]
            },
            'Max Order Size': {
                'title': 'Max Order Size',
                'all': [all_max_order_size],
                'long': [long_max_order_size],
                'short': [short_max_order_size]
            },
            'Total Closed Trades': {
                'title': 'Total Closed Trades',
                'all': [all_total_closed_trades],
                'long': [long_total_closed_trades],
                'short': [short_total_closed_trades]
            },
            'Number of Winning Trades': {
                'title': 'Number of Winning Trades',
                'all': [all_number_winning_trades],
                'long': [long_number_winning_trades],
                'short': [short_number_winning_trades]
            },
            'Number of Losing Trades': {
                'title': 'Number of Losing Trades',
                'all': [all_number_losing_trades],
                'long': [long_number_losing_trades],
                'short': [short_number_losing_trades]
            },
            'Winning Trade Percentage': {
                'title': 'Winning Trade Percentage',
                'all': [_fmt2(all_percent_profitable)],
                'long': [_fmt2(long_percent_profitable)],
                'short': [_fmt2(short_percent_profitable)]
            },
            'Average per Trade': {
                'title': 'Average per Trade',
                'all': [
                    _fmt2(all_avg_trade),
                    _fmt2(all_avg_trade_pct)
                ],
                'long': [
                    _fmt2(long_avg_trade),
                    _fmt2(long_avg_trade_pct)
                ],
                'short': [
                    _fmt2(short_avg_trade),
                    _fmt2(short_avg_trade_pct)
                ]
            },
            'Average Profit per Trade': {
                'title': 'Average Profit per Trade',
                'all': [
                    _fmt2(all_avg_winning_trade),
                    _fmt2(all_avg_winning_trade_pct)
                ],
                'long': [
                    _fmt2(long_avg_winning_trade),
                    _fmt2(long_avg_winning_trade_pct)
                ],
                'short': [
                    _fmt2(short_avg_winning_trade),
                    _fmt2(short_avg_winning_trade_pct)
                ]
            },
            'Average Loss per Trade': {
                'title': 'Average Loss per Trade',
                'all': [
                    _fmt2(all_avg_losing_trade),
                    _fmt2(all_avg_losing_trade_pct)
                ],
                'long': [
                    _fmt2(long_avg_losing_trade),
                    _fmt2(long_avg_losing_trade_pct)
                ],
                'short': [
                    _fmt2(short_avg_losing_trade),
                    _fmt2(short_avg_losing_trade_pct)
                ]
            },
            'Average Win / Average Loss Ratio': {
                'title': 'Average Win / Average Loss Ratio',
                'all': [_fmt2(all_ratio_avg_win_loss)],
                'long': [_fmt2(long_ratio_avg_win_loss)],
                'short': [_fmt2(short_ratio_avg_win_loss)]
            },
            'Largest Winning Trade': {
                'title': 'Largest Winning Trade',
                'all': [
                    _fmt2(all_largest_winning_trade),
                    _fmt2(all_largest_winning_trade_pct)
                ],
                'long': [
                    _fmt2(long_largest_winning_trade),
                    _fmt2(long_largest_winning_trade_pct)
                ],
                'short': [
                    _fmt2(short_largest_winning_trade),
                    _fmt2(short_largest_winning_trade_pct)
                ]
            },
            'Largest Losing Trade': {
                'title': 'Largest Losing Trade',
                'all': [
                    _fmt2(all_largest_losing_trade),
                    _fmt2(all_largest_losing_trade_pct)
                ],
                'long': [
                    _fmt2(long_largest_losing_trade),
                    _fmt2(long_largest_losing_trade_pct)
                ],
                'short': [
                    _fmt2(short_largest_losing_trade),
                    _fmt2(short_largest_losing_trade_pct)
                ]
            },
            'Max Equity Run-Up': {
                'title': 'Max Equity Run-Up',
                'all': [
                    _fmt2(all_max_runup),
                    _fmt2(all_max_runup_pct)
                ],
                'long': [],
                'short': [] 
            },
            'Max Equity Drawdown': {
                'title': 'Max Equity Drawdown',
                'all': [
                    _fmt2(all_max_drawdown),
                    _fmt2(all_max_drawdown_pct)
                ],
                'long': [],
                'short': []
            },
            'Recovery Factor': {
                'title': 'Recovery Factor',
                'all': [_fmt3(all_recovery_factor)],
                'long': [],
                'short': []
            },
            'Sharpe Ratio': {
                'title': 'Sharpe Ratio',
                'all': [_fmt3(all_sharpe_ratio)],
                'long': [],
                'short': []
            },
            'Sortino Ratio': {
                'title': 'Sortino Ratio',
                'all': [_fmt3(all_sortino_ratio)],
                'long': [],
                'short': []
            },
            'Skewness': {
                'title': 'Skewness',
                'all': [_fmt3(all_skew)],
                'long': [],
                'short': []
            },
            'Number of Liquidations': {
                'title': 'Number of Liquidations',
                'all': [all_liquidations_number],
                'long': [long_liquidations_number],
                'short': [short_liquidations_number]
            },
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_metrics(
        initial_capital: float,
        deals_log: np.ndarray
    ) -> tuple:
        """
        JIT-compiled function to calculate all metrics from deal logs.
        
        Args:
            initial_capital: Starting capital amount
            deals_log: Array of completed trades with structured columns
            
        Returns:
            tuple: All calculated metrics as numeric values
        """

        if deals_log.shape[0] == 0:
            # Return empty/default values for all metrics
            equity = np.array([initial_capital], dtype=np.float64)
            nan_val = np.nan
            zero_val = 0.0
            
            return (
                equity,
                # Gross Profit
                zero_val, zero_val, zero_val, zero_val, zero_val, zero_val,
                # Gross Loss  
                zero_val, zero_val, zero_val, zero_val, zero_val, zero_val,
                # Net Profit
                zero_val, zero_val, zero_val, zero_val, zero_val, zero_val,
                # Profit Factor
                nan_val, nan_val, nan_val,
                # Commission
                zero_val, zero_val, zero_val,
                # Max Order Size
                nan_val, nan_val, nan_val,
                # Trade counts
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                # Percentages and averages
                nan_val, nan_val, nan_val,
                nan_val, nan_val, nan_val, nan_val, nan_val, nan_val,
                nan_val, nan_val, nan_val, nan_val, nan_val, nan_val,
                nan_val, nan_val, nan_val, nan_val, nan_val, nan_val,
                # Ratios
                nan_val, nan_val, nan_val,
                # Largest trades
                nan_val, nan_val, nan_val, nan_val, nan_val, nan_val,
                nan_val, nan_val, nan_val, nan_val, nan_val, nan_val,
                # Risk metrics
                zero_val, zero_val, zero_val, zero_val,
                nan_val, nan_val, nan_val, nan_val,
                # Liquidations
                0, 0, 0
            )

        # Extract columns
        log_col_0 = deals_log[:, 0]    # direction
        log_col_2 = deals_log[:, 2]    # exit signal
        log_col_7 = deals_log[:, 7]    # position size
        log_col_8 = deals_log[:, 8]    # P&L currency
        log_col_9 = deals_log[:, 9]    # P&L percentage
        log_col_12 = deals_log[:, 12]  # commission

        # Create masks
        long_mask = log_col_0 == 0
        short_mask = log_col_0 == 1
        win_mask = log_col_8 > 0
        loss_mask = log_col_8 <= 0

        # Equity calculation
        equity = np.empty(log_col_8.shape[0] + 1, dtype=np.float64)
        equity[0] = initial_capital
        equity[1:] = log_col_8
        equity = np.cumsum(equity)

        # Gross Profit calculations
        win_pnl = log_col_8[win_mask]
        all_gross_profit = (
            np.sum(win_pnl)
            if win_pnl.shape[0] > 0 else 0.0
        )
        all_gross_profit_pct = (
            (all_gross_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        long_win_pnl = log_col_8[win_mask & long_mask]
        long_gross_profit = (
            np.sum(long_win_pnl)
            if long_win_pnl.shape[0] > 0 else 0.0
        )
        long_gross_profit_pct = (
            (long_gross_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        short_win_pnl = log_col_8[win_mask & short_mask]
        short_gross_profit = (
            np.sum(short_win_pnl)
            if short_win_pnl.shape[0] > 0 else 0.0
        )
        short_gross_profit_pct = (
            (short_gross_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        # Gross Loss calculations  
        loss_pnl = log_col_8[loss_mask]
        all_gross_loss = (
            abs(np.sum(loss_pnl))
            if loss_pnl.shape[0] > 0 else 0.0
        )
        all_gross_loss_pct = (
            (all_gross_loss / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        long_loss_pnl = log_col_8[loss_mask & long_mask]
        long_gross_loss = (
            abs(np.sum(long_loss_pnl))
            if long_loss_pnl.shape[0] > 0 else 0.0
        )
        long_gross_loss_pct = (
            (long_gross_loss / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        short_loss_pnl = log_col_8[loss_mask & short_mask]
        short_gross_loss = (
            abs(np.sum(short_loss_pnl))
            if short_loss_pnl.shape[0] > 0 else 0.0
        )
        short_gross_loss_pct = (
            (short_gross_loss / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        # Net Profit calculations
        all_net_profit = all_gross_profit - all_gross_loss
        all_net_profit_pct = (
            (all_net_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        long_net_profit = long_gross_profit - long_gross_loss
        long_net_profit_pct = (
            (long_net_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        short_net_profit = short_gross_profit - short_gross_loss
        short_net_profit_pct = (
            (short_net_profit / initial_capital * 100.0)
            if initial_capital != 0 else 0.0
        )

        # Profit Factor calculations
        all_profit_factor = (
            (all_gross_profit / all_gross_loss)
            if all_gross_loss != 0 else np.nan
        )
        long_profit_factor = (
            (long_gross_profit / long_gross_loss)
            if long_gross_loss != 0 else np.nan
        )
        short_profit_factor = (
            (short_gross_profit / short_gross_loss)
            if short_gross_loss != 0 else np.nan
        )

        # Commission calculations
        all_commission_paid = np.sum(log_col_12)
        long_commission_paid = np.sum(log_col_12[long_mask])
        short_commission_paid = np.sum(log_col_12[short_mask])

        # Max Order Size calculations
        all_max_order_size = (
            np.max(log_col_7)
            if log_col_7.shape[0] > 0 else np.nan
        )
        long_max_order_size = (
            np.max(log_col_7[long_mask])
            if np.sum(long_mask) > 0 else np.nan
        )
        short_max_order_size = (
            np.max(log_col_7[short_mask])
            if np.sum(short_mask) > 0 else np.nan
        )

        # Trade count calculations
        all_total_closed_trades = deals_log.shape[0]
        long_total_closed_trades = np.sum(long_mask)
        short_total_closed_trades = np.sum(short_mask)

        all_number_winning_trades = np.sum(win_mask)
        long_number_winning_trades = np.sum(win_mask & long_mask)
        short_number_winning_trades = np.sum(win_mask & short_mask)

        all_number_losing_trades = np.sum(loss_mask)
        long_number_losing_trades = np.sum(loss_mask & long_mask)
        short_number_losing_trades = np.sum(loss_mask & short_mask)

        # Winning percentage calculations
        all_percent_profitable = (
            (all_number_winning_trades / all_total_closed_trades * 100.0)
            if all_total_closed_trades > 0 else np.nan
        )
        long_percent_profitable = (
            (long_number_winning_trades / long_total_closed_trades * 100.0)
            if long_total_closed_trades > 0 else np.nan
        )
        short_percent_profitable = (
            (short_number_winning_trades / short_total_closed_trades * 100.0)
            if short_total_closed_trades > 0 else np.nan
        )

        # Average trade calculations
        all_avg_trade = (
            np.mean(log_col_8)
            if log_col_8.shape[0] > 0 else np.nan
        )
        all_avg_trade_pct = (
            np.mean(log_col_9)
            if log_col_9.shape[0] > 0 else np.nan
        )

        long_pnl_8 = log_col_8[long_mask]
        long_pnl_9 = log_col_9[long_mask]
        long_avg_trade = (
            np.mean(long_pnl_8)
            if long_pnl_8.shape[0] > 0 else np.nan
        )
        long_avg_trade_pct = (
            np.mean(long_pnl_9)
            if long_pnl_9.shape[0] > 0 else np.nan
        )

        short_pnl_8 = log_col_8[short_mask]
        short_pnl_9 = log_col_9[short_mask]
        short_avg_trade = (
            np.mean(short_pnl_8)
            if short_pnl_8.shape[0] > 0 else np.nan
        )
        short_avg_trade_pct = (
            np.mean(short_pnl_9)
            if short_pnl_9.shape[0] > 0 else np.nan
        )

        # Average winning trade calculations
        win_pnl_8 = log_col_8[win_mask]
        win_pnl_9 = log_col_9[win_mask]
        all_avg_winning_trade = (
            np.mean(win_pnl_8)
            if win_pnl_8.shape[0] > 0 else np.nan
        )
        all_avg_winning_trade_pct = (
            np.mean(win_pnl_9)
            if win_pnl_9.shape[0] > 0 else np.nan
        )

        long_win_pnl_8 = log_col_8[win_mask & long_mask]
        long_win_pnl_9 = log_col_9[win_mask & long_mask]
        long_avg_winning_trade = (
            np.mean(long_win_pnl_8)
            if long_win_pnl_8.shape[0] > 0 else np.nan
        )
        long_avg_winning_trade_pct = (
            np.mean(long_win_pnl_9)
            if long_win_pnl_9.shape[0] > 0 else np.nan
        )

        short_win_pnl_8 = log_col_8[win_mask & short_mask]
        short_win_pnl_9 = log_col_9[win_mask & short_mask]
        short_avg_winning_trade = (
            np.mean(short_win_pnl_8)
            if short_win_pnl_8.shape[0] > 0 else np.nan
        )
        short_avg_winning_trade_pct = (
            np.mean(short_win_pnl_9)
            if short_win_pnl_9.shape[0] > 0 else np.nan
        )

        # Average losing trade calculations
        loss_pnl_8 = log_col_8[loss_mask]
        loss_pnl_9 = log_col_9[loss_mask]
        all_avg_losing_trade = (
            abs(np.mean(loss_pnl_8))
            if loss_pnl_8.shape[0] > 0 else np.nan
        )
        all_avg_losing_trade_pct = (
            abs(np.mean(loss_pnl_9))
            if loss_pnl_9.shape[0] > 0 else np.nan
        )

        long_loss_pnl_8 = log_col_8[loss_mask & long_mask]
        long_loss_pnl_9 = log_col_9[loss_mask & long_mask]
        long_avg_losing_trade = (
            abs(np.mean(long_loss_pnl_8))
            if long_loss_pnl_8.shape[0] > 0 else np.nan
        )
        long_avg_losing_trade_pct = (
            abs(np.mean(long_loss_pnl_9))
            if long_loss_pnl_9.shape[0] > 0 else np.nan
        )

        short_loss_pnl_8 = log_col_8[loss_mask & short_mask]
        short_loss_pnl_9 = log_col_9[loss_mask & short_mask]
        short_avg_losing_trade = (
            abs(np.mean(short_loss_pnl_8))
            if short_loss_pnl_8.shape[0] > 0 else np.nan
        )
        short_avg_losing_trade_pct = (
            abs(np.mean(short_loss_pnl_9))
            if short_loss_pnl_9.shape[0] > 0 else np.nan
        )

        # Win/Loss ratio calculations
        all_ratio_avg_win_loss = (
            (all_avg_winning_trade / all_avg_losing_trade)
            if (
                not np.isnan(all_avg_winning_trade) and
                not np.isnan(all_avg_losing_trade) and
                all_avg_losing_trade != 0
            )
            else np.nan
        )
        long_ratio_avg_win_loss = (
            (long_avg_winning_trade / long_avg_losing_trade)
            if (
                not np.isnan(long_avg_winning_trade) and
                not np.isnan(long_avg_losing_trade) and
                long_avg_losing_trade != 0
            )
            else np.nan
        )
        short_ratio_avg_win_loss = (
            (short_avg_winning_trade / short_avg_losing_trade)
            if (
                not np.isnan(short_avg_winning_trade) and
                not np.isnan(short_avg_losing_trade) and
                short_avg_losing_trade != 0
            )
            else np.nan
        )

        # Largest winning trade calculations
        all_largest_winning_trade = (
            np.max(log_col_8)
            if log_col_8.shape[0] > 0 else np.nan
        )
        all_largest_winning_trade_pct = (
            np.max(log_col_9)
            if log_col_9.shape[0] > 0 else np.nan
        )

        long_largest_winning_trade = (
            np.max(log_col_8[long_mask])
            if np.sum(long_mask) > 0 else np.nan
        )
        long_largest_winning_trade_pct = (
            np.max(log_col_9[long_mask])
            if np.sum(long_mask) > 0 else np.nan
        )

        short_largest_winning_trade = (
            np.max(log_col_8[short_mask])
            if np.sum(short_mask) > 0 else np.nan
        )
        short_largest_winning_trade_pct = (
            np.max(log_col_9[short_mask])
            if np.sum(short_mask) > 0 else np.nan
        )

        # Largest losing trade calculations
        all_largest_losing_trade = (
            abs(np.min(log_col_8))
            if log_col_8.shape[0] > 0 else np.nan
        )
        all_largest_losing_trade_pct = (
            abs(np.min(log_col_9))
            if log_col_9.shape[0] > 0 else np.nan
        )

        long_largest_losing_trade = (
            abs(np.min(log_col_8[long_mask]))
            if np.sum(long_mask) > 0 else np.nan
        )
        long_largest_losing_trade_pct = (
            abs(np.min(log_col_9[long_mask]))
            if np.sum(long_mask) > 0 else np.nan
        )

        short_largest_losing_trade = (
            abs(np.min(log_col_8[short_mask]))
            if np.sum(short_mask) > 0 else np.nan
        )
        short_largest_losing_trade_pct = (
            abs(np.min(log_col_9[short_mask]))
            if np.sum(short_mask) > 0 else np.nan
        )

        # Max Equity Run-Up
        min_equity = equity[0]
        all_max_runup = 0.0
        all_max_runup_pct = 0.0
        for i in range(1, equity.shape[0]):
            if equity[i] < min_equity:
                min_equity = equity[i]
            if equity[i] > equity[i - 1]:
                runup = equity[i] - min_equity
                runup_pct = (equity[i] / min_equity - 1.0) * 100.0
                if runup > all_max_runup:
                    all_max_runup = runup
                if runup_pct > all_max_runup_pct:
                    all_max_runup_pct = runup_pct

        # Max Equity Drawdown
        max_equity = equity[0]
        all_max_drawdown = 0.0
        all_max_drawdown_pct = 0.0
        for i in range(1, equity.shape[0]):
            if equity[i] > max_equity:
                max_equity = equity[i]
            if equity[i] < equity[i - 1]:
                min_eq = equity[i]
                drawdown = max_equity - min_eq
                drawdown_pct = -(min_eq / max_equity - 1.0) * 100.0
                if drawdown > all_max_drawdown:
                    all_max_drawdown = drawdown
                if drawdown_pct > all_max_drawdown_pct:
                    all_max_drawdown_pct = drawdown_pct

        # Recovery Factor
        all_recovery_factor = (
            (all_net_profit / all_max_drawdown)
            if all_max_drawdown > 0 else np.nan
        )

        # Sharpe Ratio
        if log_col_9.shape[0] == 0 or np.any(np.isnan(log_col_9)):
            all_sharpe_ratio = np.nan
        else:
            excess_std = np.std(log_col_9)
            if excess_std == 0 or np.isnan(excess_std):
                all_sharpe_ratio = np.nan
            else:
                sharpe_avg_return = np.mean(log_col_9)
                all_sharpe_ratio = sharpe_avg_return / excess_std

        # Sortino Ratio
        neg_returns = log_col_9[loss_mask]
        denom = (
            np.sqrt(np.mean(neg_returns ** 2))
            if neg_returns.shape[0] > 0 else np.nan
        )
        if denom == 0 or np.isnan(denom):
            all_sortino_ratio = np.nan
        else:
            all_sortino_ratio = all_avg_trade_pct / denom

        # Skewness
        if log_col_9.shape[0] < 3:
            all_skew = np.nan
        else:
            mean_r = np.mean(log_col_9)
            std_r = np.std(log_col_9)
            if std_r == 0 or np.isnan(std_r):
                all_skew = np.nan
            else:
                all_skew = (
                    np.sum(((log_col_9 - mean_r) / std_r) ** 3)
                    / log_col_9.shape[0]
                )

        # Liquidations
        long_liquidations_number = np.sum(log_col_2 == 700)
        short_liquidations_number = np.sum(log_col_2 == 800)
        all_liquidations_number = (
            long_liquidations_number + short_liquidations_number
        )

        return (
            equity,

            # Gross Profit
            all_gross_profit,
            all_gross_profit_pct,
            long_gross_profit,
            long_gross_profit_pct,
            short_gross_profit,
            short_gross_profit_pct,

            # Gross Loss
            all_gross_loss,
            all_gross_loss_pct,
            long_gross_loss,
            long_gross_loss_pct,
            short_gross_loss,
            short_gross_loss_pct,

            # Net Profit
            all_net_profit,
            all_net_profit_pct,
            long_net_profit,
            long_net_profit_pct,
            short_net_profit,
            short_net_profit_pct,

            # Profit Factor
            all_profit_factor,
            long_profit_factor,
            short_profit_factor,

            # Commission
            all_commission_paid,
            long_commission_paid,
            short_commission_paid,

            # Max Order Size
            all_max_order_size,
            long_max_order_size,
            short_max_order_size,

            # Trade counts
            all_total_closed_trades,
            long_total_closed_trades,
            short_total_closed_trades,
            all_number_winning_trades,
            long_number_winning_trades,
            short_number_winning_trades,
            all_number_losing_trades,
            long_number_losing_trades,
            short_number_losing_trades,

            # Percentages and averages
            all_percent_profitable,
            long_percent_profitable,
            short_percent_profitable,
            all_avg_trade,
            all_avg_trade_pct,
            long_avg_trade,
            long_avg_trade_pct,
            short_avg_trade,
            short_avg_trade_pct,
            all_avg_winning_trade,
            all_avg_winning_trade_pct,
            long_avg_winning_trade,
            long_avg_winning_trade_pct,
            short_avg_winning_trade,
            short_avg_winning_trade_pct,
            all_avg_losing_trade,
            all_avg_losing_trade_pct,
            long_avg_losing_trade,
            long_avg_losing_trade_pct,
            short_avg_losing_trade,
            short_avg_losing_trade_pct,

            # Ratios
            all_ratio_avg_win_loss,
            long_ratio_avg_win_loss,
            short_ratio_avg_win_loss,

            # Largest trades
            all_largest_winning_trade,
            all_largest_winning_trade_pct,
            long_largest_winning_trade,
            long_largest_winning_trade_pct,
            short_largest_winning_trade,
            short_largest_winning_trade_pct,
            all_largest_losing_trade,
            all_largest_losing_trade_pct,
            long_largest_losing_trade,
            long_largest_losing_trade_pct,
            short_largest_losing_trade,
            short_largest_losing_trade_pct,

            # Risk metrics
            all_max_runup,
            all_max_runup_pct,
            all_max_drawdown,
            all_max_drawdown_pct,
            all_recovery_factor,
            all_sharpe_ratio,
            all_sortino_ratio,
            all_skew,

            # Liquidations
            all_liquidations_number,
            long_liquidations_number,
            short_liquidations_number
        )
    
    def _get_empty_metrics_structure(self) -> StrategyMetrics:
        """
        Create empty metrics when no data.
        
        Returns:
            StrategyMetrics: Empty metrics structure with proper format
        """
        
        return {
            'overview': {
                'primary': [],
                'equity': np.array([])
            },
            'performance': [],
            'trades': [],
            'risk': []
        }