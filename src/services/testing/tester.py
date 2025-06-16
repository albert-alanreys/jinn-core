from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from src.core.strategy.base_strategy import BaseStrategy


class Tester:
    @staticmethod
    def test(strategy_instance: 'BaseStrategy') -> dict:
        return {
            'equity': Tester._get_equity(
                initial_capital=strategy_instance.params['initial_capital'],
                deals_log=strategy_instance.completed_deals_log
            ),
            'metrics': Tester._get_metrics(
                initial_capital=strategy_instance.params['initial_capital'],
                deals_log=strategy_instance.completed_deals_log
            )
        }

    @staticmethod
    def _get_equity(
        initial_capital: float,
        deals_log: np.ndarray
    ) -> np.ndarray:
        log = deals_log.reshape((-1, 13))

        equity = np.empty(log.shape[0] + 1)
        equity[0] = initial_capital
        equity[1:] = log[:, 8]
        return equity.cumsum()[1:]

    @staticmethod
    def _get_metrics(initial_capital: float, deals_log: np.ndarray) -> list:
        def _mean(array: np.ndarray) -> float:
            return round(array.mean(), 2) if array.size else np.nan

        log = deals_log.reshape((-1, 13))

        log_col_0 = log[:, 0]
        log_col_8 = log[:, 8]
        log_col_9 = log[:, 9]
        log_col_12 = log[:, 12]

        # Gross profit
        all_gross_profit = round(log_col_8[log_col_8 > 0].sum(), 2)
        all_gross_profit_per = round(
            all_gross_profit / initial_capital * 100, 2
        )

        long_gross_profit = round(
            log_col_8[(log_col_8 > 0) & (log_col_0 == 0)].sum(),
            2
        )
        long_gross_profit_per = round(
            long_gross_profit / initial_capital * 100,
            2
        )

        short_gross_profit = round(
            log_col_8[(log_col_8 > 0) & (log_col_0 == 1)].sum(),
            2
        )
        short_gross_profit_per = round(
            short_gross_profit / initial_capital * 100,
            2
        )

        # Gross loss
        all_gross_loss = round(abs(log_col_8[log_col_8 <= 0].sum()), 2)
        all_gross_loss_per = round(
            all_gross_loss / initial_capital * 100, 2
        )

        long_gross_loss = round(
            abs(log_col_8[(log_col_8 <= 0) & (log_col_0 == 0)].sum()),
            2
        )
        long_gross_loss_per = round(
            long_gross_loss / initial_capital * 100,
            2
        )

        short_gross_loss = round(
            abs(log_col_8[(log_col_8 <= 0) & (log_col_0 == 1)].sum()),
            2
        )
        short_gross_loss_per = round(
            short_gross_loss / initial_capital * 100,
            2
        )

        # Net profit
        all_net_profit = round(all_gross_profit - all_gross_loss, 2)
        all_net_profit_per = round(
            all_net_profit / initial_capital * 100,
            2
        )

        long_net_profit = round(long_gross_profit - long_gross_loss, 2)
        long_net_profit_per = round(
            long_net_profit / initial_capital * 100,
            2
        )

        short_net_profit = round(short_gross_profit - short_gross_loss, 2)
        short_net_profit_per = round(
            short_net_profit / initial_capital * 100,
            2
        )

        # Profit factor
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

        # Commission paid
        all_commission_paid = round(log_col_12.sum(), 2)
        long_commission_paid = round(log_col_12[log_col_0 == 0].sum(), 2)
        short_commission_paid = round(log_col_12[log_col_0 == 1].sum(), 2)

        # Total closed trades
        all_total_closed_trades = log.shape[0]
        long_total_closed_trades = log[log_col_0 == 0].shape[0]
        short_total_closed_trades = log[log_col_0 == 1].shape[0]

        # Number winning trades
        all_number_winning_trades = log[log_col_8 > 0].shape[0]
        long_number_winning_trades = log[
            (log_col_8 > 0) & (log_col_0 == 0)
        ].shape[0]
        short_number_winning_trades = log[
            (log_col_8 > 0) & (log_col_0 == 1)
        ].shape[0]

        # Number losing trades
        all_number_losing_trades = log[log_col_8 <= 0].shape[0]
        long_number_losing_trades = log[
            (log_col_8 <= 0) & (log_col_0 == 0)
        ].shape[0]
        short_number_losing_trades = log[
            (log_col_8 <= 0) & (log_col_0 == 1)
        ].shape[0]

        # Percent profitable
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

        # Avg trade
        all_avg_trade = _mean(log_col_8)
        all_avg_trade_per = _mean(log_col_9)

        long_avg_trade = _mean(log_col_8[log_col_0 == 0])
        long_avg_trade_per = _mean(log_col_9[log_col_0 == 0])

        short_avg_trade = _mean(log_col_8[log_col_0 == 1])
        short_avg_trade_per = _mean(log_col_9[log_col_0 == 1])

        # Avg winning trade
        all_avg_winning_trade = _mean(log_col_8[log_col_8 > 0])
        all_avg_winning_trade_per = _mean(log_col_9[log_col_9 > 0])

        long_avg_winning_trade = _mean(
            log_col_8[(log_col_8 > 0) & (log_col_0 == 0)]
        )
        long_avg_winning_trade_per = _mean(
            log_col_9[(log_col_9 > 0) & (log_col_0 == 0)]
        )

        short_avg_winning_trade = _mean(
            log_col_8[(log_col_8 > 0) & (log_col_0 == 1)]
        )
        short_avg_winning_trade_per = _mean(
            log_col_9[(log_col_9 > 0) & (log_col_0 == 1)]
        )

        # Avg losing trade
        all_avg_losing_trade = abs(_mean(log_col_8[log_col_8 <= 0]))
        all_avg_losing_trade_per = abs(_mean(log_col_9[log_col_9 <= 0]))

        long_avg_losing_trade = abs(
            _mean(log_col_8[(log_col_8 <= 0) & (log_col_0 == 0)])
        )
        long_avg_losing_trade_per = abs(
            _mean(log_col_9[(log_col_9 <= 0) & (log_col_0 == 0)])
        )

        short_avg_losing_trade = abs(
            _mean(log_col_8[(log_col_8 <= 0) & (log_col_0 == 1)])
        )
        short_avg_losing_trade_per = abs(
            _mean(log_col_9[(log_col_9 <= 0) & (log_col_0 == 1)])
        )

        # Ratio avg win / avg loss
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

        # Largest winning trade
        all_largest_winning_trade = np.nan
        all_largest_winning_trade_per = np.nan

        try:
            all_largest_winning_trade = round(log_col_8.max(), 2)
            all_largest_winning_trade_per = round(log_col_9.max(), 2)
        except Exception:
            pass

        long_largest_winning_trade = np.nan
        long_largest_winning_trade_per = np.nan

        try:
            long_largest_winning_trade = round(
                log_col_8[log_col_0 == 0].max(),
                2
            )
            long_largest_winning_trade_per = round(
                log_col_9[log_col_0 == 0].max(),
                2
            )
        except Exception:
            pass

        short_largest_winning_trade = np.nan
        short_largest_winning_trade_per = np.nan

        try:
            short_largest_winning_trade = round(
                log_col_8[log_col_0 == 1].max(),
                2
            )
            short_largest_winning_trade_per = round(
                log_col_9[log_col_0 == 1].max(),
                2
            )
        except Exception:
            pass

        # Largest losing trade
        all_largest_losing_trade = np.nan
        all_largest_losing_trade_per = np.nan

        try:
            all_largest_losing_trade = round(abs(log_col_8.min()), 2)
            all_largest_losing_trade_per = round(abs(log_col_9.min()), 2)
        except Exception:
            pass

        long_largest_losing_trade = np.nan
        long_largest_losing_trade_per = np.nan  

        try:
            long_largest_losing_trade = round(
                abs(log_col_8[log_col_0 == 0].min()),
                2
            )
            long_largest_losing_trade_per = round(
                abs(log_col_9[log_col_0 == 0].min()),
                2
            )
        except Exception:
            pass

        short_largest_losing_trade = np.nan
        short_largest_losing_trade_per = np.nan

        try:
            short_largest_losing_trade = round(
                abs(log_col_8[log_col_0 == 1].min()),
                2
            )
            short_largest_losing_trade_per = round(
                abs(log_col_9[log_col_0 == 1].min()),
                2
            )
        except Exception:
            pass

        # Max drawdown
        try:
            equity = np.concatenate(
                (np.array([initial_capital]), log_col_8)
            ).cumsum()
            max_equity = equity[0]
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

            for i in range(1, equity.shape[0]):
                if equity[i] > max_equity:
                    max_equity = equity[i]

                if equity[i] < equity[i - 1]:
                    min_equity = equity[i]
                    drawdown = max_equity - min_equity
                    drawdown_per = -(min_equity / max_equity - 1) * 100

                    if drawdown > all_max_drawdown:
                        all_max_drawdown = round(drawdown, 2)

                    if drawdown_per > all_max_drawdown_per:
                        all_max_drawdown_per = round(drawdown_per, 2)
        except Exception:
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

        # Sortino ratio
        denominator = _mean(log_col_9[log_col_9 <= 0] ** 2) ** 0.5

        if denominator == 0 or np.isnan(denominator):
            all_sortino_ratio = np.nan 
        else:
            all_sortino_ratio = round(all_avg_trade_per / denominator, 3)

        return [
            {
                'title': 'Чистая прибыль',
                'all': [
                    all_net_profit,
                    all_net_profit_per
                ],
                'long': [
                    long_net_profit,
                    long_net_profit_per
                ],
                'short': [
                    short_net_profit,
                    short_net_profit_per
                ]
            },
            {
                'title': 'Валовая прибыль',
                'all': [
                    all_gross_profit,
                    all_gross_profit_per
                ],
                'long': [
                    long_gross_profit,
                    long_gross_profit_per
                ],
                'short': [
                    short_gross_profit,
                    short_gross_profit_per
                ]
            },
            {
                'title': 'Валовой убыток',
                'all': [
                    all_gross_loss,
                    all_gross_loss_per
                ],
                'long': [
                    long_gross_loss,
                    long_gross_loss_per
                ],
                'short': [
                    short_gross_loss,
                    short_gross_loss_per
                ]
            },
            {
                'title': 'Фактор прибыли',
                'all': [all_profit_factor],
                'long': [long_profit_factor],
                'short': [short_profit_factor]
            },
            {
                'title': 'Выплаченная комиссия',
                'all': [all_commission_paid],
                'long': [long_commission_paid],
                'short': [short_commission_paid]
            },
            {
                'title': 'Всего закрытых сделок',
                'all': [all_total_closed_trades],
                'long': [long_total_closed_trades],
                'short': [short_total_closed_trades]
            },
            {
                'title': 'Количество прибыльных сделок',
                'all': [all_number_winning_trades],
                'long': [long_number_winning_trades],
                'short': [short_number_winning_trades]
            },
            {
                'title': 'Количество убыточных сделок',
                'all': [all_number_losing_trades],
                'long': [long_number_losing_trades],
                'short': [short_number_losing_trades]
            },
            {
                'title': 'Процент прибыльных сделок',
                'all': [all_percent_profitable],
                'long': [long_percent_profitable],
                'short': [short_percent_profitable]
            },
            {
                'title': 'Средняя по сделке',
                'all': [
                    all_avg_trade,
                    all_avg_trade_per
                ],
                'long': [
                    long_avg_trade,
                    long_avg_trade_per
                ],
                'short': [
                    short_avg_trade,
                    short_avg_trade_per
                ]
            },
            {
                'title': 'Средняя прибыль по сделке',
                'all': [
                    all_avg_winning_trade,
                    all_avg_winning_trade_per
                ],
                'long': [
                    long_avg_winning_trade,
                    long_avg_winning_trade_per
                ],
                'short': [
                    short_avg_winning_trade,
                    short_avg_winning_trade_per
                ]
            },
            {
                'title': 'Средний убыток по сделке',
                'all': [
                    all_avg_losing_trade,
                    all_avg_losing_trade_per
                ],
                'long': [
                    long_avg_losing_trade,
                    long_avg_losing_trade_per
                ],
                'short': [
                    short_avg_losing_trade,
                    short_avg_losing_trade_per
                ]
            },
            {
                'title': 'Коэффициент средней прибыли / среднего убытка',
                'all': [all_ratio_avg_win_loss],
                'long': [long_ratio_avg_win_loss],
                'short': [short_ratio_avg_win_loss]
            },
            {
                'title': 'Самая прибыльная сделка',
                'all': [
                    all_largest_winning_trade,
                    all_largest_winning_trade_per
                ],
                'long': [
                    long_largest_winning_trade,
                    long_largest_winning_trade_per
                ],
                'short': [
                    short_largest_winning_trade,
                    short_largest_winning_trade_per
                ]
            },
            {
                'title': 'Самая убыточная сделка',
                'all': [
                    all_largest_losing_trade,
                    all_largest_losing_trade_per
                ],
                'long': [
                    long_largest_losing_trade,
                    long_largest_losing_trade_per
                ],
                'short': [
                    short_largest_losing_trade,
                    short_largest_losing_trade_per
                ]
            },
            {
                'title': 'Максимальная просадка',
                'all': [
                    all_max_drawdown,
                    all_max_drawdown_per
                ],
                'long': [],
                'short': []
            },
            {
                'title': 'Коэффициент Сортино',
                'all': [all_sortino_ratio],
                'long': [],
                'short': []
            }
        ]