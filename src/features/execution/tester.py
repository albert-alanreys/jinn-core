import numpy as np


class StrategyTester:
    """
    Core service responsible for calculating
    trading strategy metrics via backtesting.

    Processes deal logs and returns metrics in four categories:
    - Overview: Summary metrics and equity curve
    - Performance: Performance metrics
    - Trades: Trade-related metrics
    - Risk: Risk-related metrics
    """

    @staticmethod
    def test(context: dict) -> None:
        """
        Performs backtesting analysis on a strategy instance.

        Analyzes the strategy's completed deals log
        to calculate strategy metrics.

        Args:
            strategy_instance (BaseStrategy): Strategy instance containing:
                - params['initial_capital']: Starting capital amount
                - completed_deals_log: Array of completed trades

        Returns:
            dict: Dictionary with four groups of backtesting metrics:
                - overview: Summary metrics and equity curve
                - performance: Strategy performance metrics
                - trades: Trade-related execution metrics
                - risk: Risk-adjusted metrics
        """

        initial_capital = context['strategy'].params['initial_capital']
        completed_deals_log = context['strategy'].completed_deals_log

        all_metrics = StrategyTester._get_all_metrics(
            initial_capital=initial_capital,
            deals_log=completed_deals_log
        )

        overview = StrategyTester._get_overview_metrics(all_metrics)
        performance = StrategyTester._get_performance_metrics(all_metrics)
        trades = StrategyTester._get_trade_metrics(all_metrics)
        risk = StrategyTester._get_risk_metrics(all_metrics)

        context['metrics'] = {
            'overview': overview,
            'performance': performance,
            'trades': trades,
            'risk': risk,
        }

    @staticmethod
    def _get_overview_metrics(all_metrics: dict) -> list:
        """
        Extracts overview metrics.

        Args:
            all_metrics: Complete set of calculated metrics
                         from _get_all_metrics

        Returns:
            dict: Overview metrics with two sections:
                  - primary: Key strategy metrics
                  - equity: Equity curve data
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

    @staticmethod
    def _get_performance_metrics(all_metrics: dict) -> list:
        """
        Extracts performance metrics.

        Args:
            all_metrics: Complete set of calculated metrics
                         from _get_all_metrics

        Returns:
            list: List of performance metrics
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

    @staticmethod
    def _get_trade_metrics(all_metrics: dict) -> list:
        """
        Extracts trade-related metrics.

        Args:
            all_metrics: Complete set of calculated metrics
                         from _get_all_metrics

        Returns:
            list: List of trade-related metrics
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

    @staticmethod
    def _get_risk_metrics(all_metrics: dict) -> list:
        """
        Extracts risk-related metrics.

        Args:
            all_metrics: Complete set of calculated metrics
                         from _get_all_metrics

        Returns:
            list: List of risk-related metrics
        """

        return [
            all_metrics['Max Equity Drawdown'],
            all_metrics['Sharpe Ratio'],
            all_metrics['Sortino Ratio'],
            all_metrics['Skewness'],
            all_metrics['Number of Liquidations'],
        ]

    @staticmethod
    def _get_all_metrics(
        initial_capital: float,
        deals_log: np.ndarray
    ) -> list:
        """
        Calculates strategy metrics from deal logs.

        The deals_log array is expected to contain columns:
        - Column 0: Trade direction (0=long, 1=short)
        - Column 2: Exit signal (signal code)
        - Column 7: Position size (units)
        - Column 8: Trade P&L in currency units
        - Column 9: Trade P&L in percentage
        - Column 12: Commission paid

        Args:
            initial_capital (float): Starting capital amount
            deals_log (np.ndarray): Array of completed trades with columns
                                    for direction, P&L, and commission

        Returns:
            dict: Complete metrics dictionary with 'title', 'all',
                  'long', and 'short' data for each metric
        """

        def _mean(array: np.ndarray) -> float:
            return round(array.mean(), 2) if array.shape[0] else np.nan

        log_col_0 = deals_log[:, 0]
        log_col_2 = deals_log[:, 2]
        log_col_7 = deals_log[:, 7]
        log_col_8 = deals_log[:, 8]
        log_col_9 = deals_log[:, 9]
        log_col_12 = deals_log[:, 12]

        long_mask = log_col_0 == 0
        short_mask = log_col_0 == 1

        win_mask = log_col_8 > 0
        win_mask_pct = log_col_8 > 0

        loss_mask = ~win_mask
        loss_mask_pct = ~win_mask_pct

        # Equity
        equity = np.empty(log_col_8.shape[0] + 1, dtype=np.float64)
        equity[0] = initial_capital
        equity[1:] = log_col_8
        equity = equity.cumsum()[1:]

        # Gross Profit
        all_gross_profit = round(log_col_8[win_mask].sum(), 2)
        all_gross_profit_pct = round(
            all_gross_profit / initial_capital * 100, 2
        )

        long_gross_profit = round(
            log_col_8[win_mask & long_mask].sum(),
            2
        )
        long_gross_profit_pct = round(
            long_gross_profit / initial_capital * 100,
            2
        )

        short_gross_profit = round(
            log_col_8[win_mask & short_mask].sum(),
            2
        )
        short_gross_profit_pct = round(
            short_gross_profit / initial_capital * 100,
            2
        )

        # Gross Loss
        all_gross_loss = round(abs(log_col_8[loss_mask].sum()), 2)
        all_gross_loss_pct = round(
            all_gross_loss / initial_capital * 100, 2
        )

        long_gross_loss = round(
            abs(log_col_8[loss_mask & long_mask].sum()),
            2
        )
        long_gross_loss_pct = round(
            long_gross_loss / initial_capital * 100,
            2
        )

        short_gross_loss = round(
            abs(log_col_8[loss_mask & short_mask].sum()),
            2
        )
        short_gross_loss_pct = round(
            short_gross_loss / initial_capital * 100,
            2
        )

        # Net Profit
        all_net_profit = round(all_gross_profit - all_gross_loss, 2)
        all_net_profit_pct = round(
            all_net_profit / initial_capital * 100,
            2
        )

        long_net_profit = round(long_gross_profit - long_gross_loss, 2)
        long_net_profit_pct = round(
            long_net_profit / initial_capital * 100,
            2
        )

        short_net_profit = round(short_gross_profit - short_gross_loss, 2)
        short_net_profit_pct = round(
            short_net_profit / initial_capital * 100,
            2
        )

        # Profit Factor
        if all_gross_loss != 0:
            all_profit_factor = round(
                all_gross_profit / all_gross_loss,
                3
            )
        else:
            all_profit_factor = np.nan

        if long_gross_loss != 0:
            long_profit_factor =  round(
                long_gross_profit / long_gross_loss,
                3
            )
        else:
            long_profit_factor = np.nan

        if short_gross_loss != 0:
            short_profit_factor = round(
                short_gross_profit / short_gross_loss,
                3
            )
        else:
            short_profit_factor = np.nan

        # Commission Paid
        all_commission_paid = round(log_col_12.sum(), 2)
        long_commission_paid = round(log_col_12[long_mask].sum(), 2)
        short_commission_paid = round(log_col_12[short_mask].sum(), 2)

        # Max Order Size
        all_max__order_size = (
            np.max(log_col_7)
            if log_col_7.shape[0] > 0
            else np.nan
        )
        long_max__order_size = (
            np.max(log_col_7[long_mask])
            if log_col_7[long_mask].shape[0] > 0
            else np.nan
        )
        short_max__order_size = (
            np.max(log_col_7[short_mask])
            if log_col_7[short_mask].shape[0] > 0
            else np.nan
        )

        # Total Closed Trades
        all_total_closed_trades = deals_log.shape[0]
        long_total_closed_trades = deals_log[long_mask].shape[0]
        short_total_closed_trades = deals_log[short_mask].shape[0]

        # Number of Winning Trades
        all_number_winning_trades = deals_log[win_mask].shape[0]
        long_number_winning_trades = deals_log[win_mask & long_mask].shape[0]
        short_number_winning_trades = deals_log[win_mask & short_mask].shape[0]

        # Number of Losing Trades
        all_number_losing_trades = deals_log[loss_mask].shape[0]
        long_number_losing_trades = deals_log[loss_mask & long_mask].shape[0]
        short_number_losing_trades = deals_log[loss_mask & short_mask].shape[0]

        # Winning Trade Percentage
        try:
            all_percent_profitable = round(
                all_number_winning_trades / 
                    all_total_closed_trades * 100,
                2
            )
        except Exception:
            all_percent_profitable = np.nan

        try:
            long_percent_profitable = round(
                long_number_winning_trades / 
                    long_total_closed_trades * 100,
                2
            )
        except Exception:
            long_percent_profitable = np.nan

        try:
            short_percent_profitable = round(
                short_number_winning_trades / 
                    short_total_closed_trades * 100,
                2
            )
        except Exception:
            short_percent_profitable = np.nan

        # Average per Trade
        all_avg_trade = _mean(log_col_8)
        all_avg_trade_pct = _mean(log_col_9)

        long_avg_trade = _mean(log_col_8[long_mask])
        long_avg_trade_pct = _mean(log_col_9[long_mask])

        short_avg_trade = _mean(log_col_8[short_mask])
        short_avg_trade_pct = _mean(log_col_9[short_mask])

        # Average Profit per Trade
        all_avg_winning_trade = _mean(log_col_8[win_mask])
        all_avg_winning_trade_pct = _mean(log_col_9[win_mask_pct])

        long_avg_winning_trade = _mean(
            log_col_8[win_mask & long_mask]
        )
        long_avg_winning_trade_pct = _mean(
            log_col_9[(win_mask_pct) & long_mask]
        )

        short_avg_winning_trade = _mean(
            log_col_8[win_mask & short_mask]
        )
        short_avg_winning_trade_pct = _mean(
            log_col_9[(win_mask_pct) & short_mask]
        )

        # Average Loss per Trade
        all_avg_losing_trade = abs(_mean(log_col_8[loss_mask]))
        all_avg_losing_trade_pct = abs(_mean(log_col_9[loss_mask_pct]))

        long_avg_losing_trade = abs(
            _mean(log_col_8[loss_mask & long_mask])
        )
        long_avg_losing_trade_pct = abs(
            _mean(log_col_9[(loss_mask_pct) & long_mask])
        )

        short_avg_losing_trade = abs(
            _mean(log_col_8[loss_mask & short_mask])
        )
        short_avg_losing_trade_pct = abs(
            _mean(log_col_9[(loss_mask_pct) & short_mask])
        )

        # Average Win / Average Loss Ratio
        all_ratio_avg_win_loss = round(
            all_avg_winning_trade / all_avg_losing_trade,
            3
        )
        long_ratio_avg_win_loss = round(
            long_avg_winning_trade / long_avg_losing_trade,
            3
        )
        short_ratio_avg_win_loss = round(
            short_avg_winning_trade / short_avg_losing_trade,
            3
        )

        # Largest Winning Trade
        all_largest_winning_trade = np.nan
        all_largest_winning_trade_pct = np.nan

        try:
            all_largest_winning_trade = round(log_col_8.max(), 2)
            all_largest_winning_trade_pct = round(log_col_9.max(), 2)
        except Exception:
            pass

        long_largest_winning_trade = np.nan
        long_largest_winning_trade_pct = np.nan

        try:
            long_largest_winning_trade = round(
                log_col_8[long_mask].max(),
                2
            )
            long_largest_winning_trade_pct = round(
                log_col_9[long_mask].max(),
                2
            )
        except Exception:
            pass

        short_largest_winning_trade = np.nan
        short_largest_winning_trade_pct = np.nan

        try:
            short_largest_winning_trade = round(
                log_col_8[short_mask].max(),
                2
            )
            short_largest_winning_trade_pct = round(
                log_col_9[short_mask].max(),
                2
            )
        except Exception:
            pass

        # Largest Losing Trade
        all_largest_losing_trade = np.nan
        all_largest_losing_trade_pct = np.nan

        try:
            all_largest_losing_trade = round(abs(log_col_8.min()), 2)
            all_largest_losing_trade_pct = round(abs(log_col_9.min()), 2)
        except Exception:
            pass

        long_largest_losing_trade = np.nan
        long_largest_losing_trade_pct = np.nan  

        try:
            long_largest_losing_trade = round(
                abs(log_col_8[long_mask].min()),
                2
            )
            long_largest_losing_trade_pct = round(
                abs(log_col_9[long_mask].min()),
                2
            )
        except Exception:
            pass

        short_largest_losing_trade = np.nan
        short_largest_losing_trade_pct = np.nan

        try:
            short_largest_losing_trade = round(
                abs(log_col_8[short_mask].min()),
                2
            )
            short_largest_losing_trade_pct = round(
                abs(log_col_9[short_mask].min()),
                2
            )
        except Exception:
            pass

        # Max Equity Run-Up
        try:
            equity = np.concatenate(
                (np.array([initial_capital]), log_col_8)
            ).cumsum()

            min_equity = equity[0]
            all_max_runup = 0.0
            all_max_runup_pct = 0.0

            for i in range(1, equity.shape[0]):
                if equity[i] < min_equity:
                    min_equity = equity[i]

                if equity[i] > equity[i - 1]:
                    runup = equity[i] - min_equity
                    runup_pct = (equity[i] / min_equity - 1) * 100

                    if runup > all_max_runup:
                        all_max_runup = round(runup, 2)

                    if runup_pct > all_max_runup_pct:
                        all_max_runup_pct = round(runup_pct, 2)

        except Exception:
            all_max_runup = 0.0
            all_max_runup_pct = 0.0

        # Max drawdown
        try:
            equity = np.concatenate(
                (np.array([initial_capital]), log_col_8)
            ).cumsum()
            max_equity = equity[0]
            all_max_drawdown = 0.0
            all_max_drawdown_pct = 0.0

            for i in range(1, equity.shape[0]):
                if equity[i] > max_equity:
                    max_equity = equity[i]

                if equity[i] < equity[i - 1]:
                    min_equity = equity[i]
                    drawdown = max_equity - min_equity
                    drawdown_per = -(min_equity / max_equity - 1) * 100

                    if drawdown > all_max_drawdown:
                        all_max_drawdown = round(drawdown, 2)

                    if drawdown_per > all_max_drawdown_pct:
                        all_max_drawdown_pct = round(drawdown_per, 2)
        except Exception:
            all_max_drawdown = 0.0
            all_max_drawdown_pct = 0.0

        # Recovery Factor
        if all_max_drawdown > 0:
            all_recovery_factor = round(
                all_net_profit / all_max_drawdown,
                3
            )
        else:
            all_recovery_factor = np.nan

        # Sharpe Ratio
        if len(log_col_9) == 0 or np.any(np.isnan(log_col_9)):
            all_sharpe_ratio = np.nan
        else:
            excess_std = np.std(log_col_9)
            
            if excess_std == 0 or np.isnan(excess_std):
                all_sharpe_ratio = np.nan
            else:
                sharpe_avg_return = _mean(log_col_9)
                all_sharpe_ratio = round(sharpe_avg_return / excess_std, 3)

        # Sortino ratio
        denominator = _mean(log_col_9[loss_mask_pct] ** 2) ** 0.5

        if denominator == 0 or np.isnan(denominator):
            all_sortino_ratio = np.nan 
        else:
            all_sortino_ratio = round(all_avg_trade_pct / denominator, 3)

        # Skewness
        if log_col_9.shape[0] < 3:
            all_skew = np.nan
        else:
            mean = log_col_9.mean()
            std = log_col_9.std()

            if std == 0 or np.isnan(std):
                all_skew = np.nan
            else:
                all_skew = round(
                    np.sum(
                        ((log_col_9 - mean) / std) ** 3
                    ) / log_col_9.shape[0],
                    3
                )

        # Number of Liquidations
        long_liquidations_number = log_col_2[log_col_2 == 700].shape[0]
        short_liquidations_number = log_col_2[log_col_2 == 800].shape[0]
        all_liquidations_number = (
            long_liquidations_number + short_liquidations_number
        )

        return {
            'equity': equity,
            'Gross Profit': {
                'title': 'Gross Profit',
                'all': [
                    all_gross_profit,
                    all_gross_profit_pct
                ],
                'long': [
                    long_gross_profit,
                    long_gross_profit_pct
                ],
                'short': [
                    short_gross_profit,
                    short_gross_profit_pct
                ]
            },
            'Gross Loss': {
                'title': 'Gross Loss',
                'all': [
                    all_gross_loss,
                    all_gross_loss_pct
                ],
                'long': [
                    long_gross_loss,
                    long_gross_loss_pct
                ],
                'short': [
                    short_gross_loss,
                    short_gross_loss_pct
                ]
            },
            'Net Profit': {
                'title': 'Net Profit',
                'all': [
                    all_net_profit,
                    all_net_profit_pct
                ],
                'long': [
                    long_net_profit,
                    long_net_profit_pct
                ],
                'short': [
                    short_net_profit,
                    short_net_profit_pct
                ]
            },
            'Profit Factor': {
                'title': 'Profit Factor',
                'all': [all_profit_factor],
                'long': [long_profit_factor],
                'short': [short_profit_factor]
            },
            'Commission Paid': {
                'title': 'Commission Paid',
                'all': [all_commission_paid],
                'long': [long_commission_paid],
                'short': [short_commission_paid]
            },
            'Max Order Size': {
                'title': 'Max Order Size',
                'all': [all_max__order_size],
                'long': [long_max__order_size],
                'short': [short_max__order_size]
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
                'all': [all_percent_profitable],
                'long': [long_percent_profitable],
                'short': [short_percent_profitable]
            },
            'Average per Trade': {
                'title': 'Average per Trade',
                'all': [
                    all_avg_trade,
                    all_avg_trade_pct
                ],
                'long': [
                    long_avg_trade,
                    long_avg_trade_pct
                ],
                'short': [
                    short_avg_trade,
                    short_avg_trade_pct
                ]
            },
            'Average Profit per Trade': {
                'title': 'Average Profit per Trade',
                'all': [
                    all_avg_winning_trade,
                    all_avg_winning_trade_pct
                ],
                'long': [
                    long_avg_winning_trade,
                    long_avg_winning_trade_pct
                ],
                'short': [
                    short_avg_winning_trade,
                    short_avg_winning_trade_pct
                ]
            },
            'Average Loss per Trade': {
                'title': 'Average Loss per Trade',
                'all': [
                    all_avg_losing_trade,
                    all_avg_losing_trade_pct
                ],
                'long': [
                    long_avg_losing_trade,
                    long_avg_losing_trade_pct
                ],
                'short': [
                    short_avg_losing_trade,
                    short_avg_losing_trade_pct
                ]
            },
            'Average Win / Average Loss Ratio': {
                'title': 'Average Win / Average Loss Ratio',
                'all': [all_ratio_avg_win_loss],
                'long': [long_ratio_avg_win_loss],
                'short': [short_ratio_avg_win_loss]
            },
            'Largest Winning Trade': {
                'title': 'Largest Winning Trade',
                'all': [
                    all_largest_winning_trade,
                    all_largest_winning_trade_pct
                ],
                'long': [
                    long_largest_winning_trade,
                    long_largest_winning_trade_pct
                ],
                'short': [
                    short_largest_winning_trade,
                    short_largest_winning_trade_pct
                ]
            },
            'Largest Losing Trade': {
                'title': 'Largest Losing Trade',
                'all': [
                    all_largest_losing_trade,
                    all_largest_losing_trade_pct
                ],
                'long': [
                    long_largest_losing_trade,
                    long_largest_losing_trade_pct
                ],
                'short': [
                    short_largest_losing_trade,
                    short_largest_losing_trade_pct
                ]
            },
            'Max Equity Run-Up': {
                'title': 'Max Equity Run-Up',
                'all': [
                    all_max_runup,
                    all_max_runup_pct
                ],
                'long': [],
                'short': [] 
            },
            'Max Equity Drawdown': {
                'title': 'Max Equity Drawdown',
                'all': [
                    all_max_drawdown,
                    all_max_drawdown_pct
                ],
                'long': [],
                'short': []
            },
            'Recovery Factor': {
                'title': 'Recovery Factor',
                'all': [all_recovery_factor],
                'long': [],
                'short': []
            },
            'Sharpe Ratio': {
                'title': 'Sharpe Ratio',
                'all': [all_sharpe_ratio],
                'long': [],
                'short': []
            },
            'Sortino Ratio': {
                'title': 'Sortino Ratio',
                'all': [all_sortino_ratio],
                'long': [],
                'short': []
            },
            'Skewness': {
                'title': 'Skewness',
                'all': [all_skew],
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