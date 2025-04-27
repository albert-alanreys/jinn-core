import numpy as np


def get_performance_metrics(initial_capital: float, log: np.ndarray) -> tuple:
    log = log.reshape((-1, 13))

    equity = np.concatenate(
        (np.array([initial_capital]), log[:, 8])
    ).cumsum()
    
    # Gross profit
    all_gross_profit = round(log[:, 8][log[:, 8] > 0].sum(), 2)
    all_gross_profit_per = round(
        all_gross_profit / initial_capital * 100, 2
    )

    long_gross_profit = round(
        log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 0)].sum(), 2
    )
    long_gross_profit_per = round(
        long_gross_profit / initial_capital * 100, 2
    )

    short_gross_profit = round(
        log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 1)].sum(), 2
    )
    short_gross_profit_per = round(
        short_gross_profit / initial_capital * 100, 2
    )

    # Gross loss
    all_gross_loss = round(abs(log[:, 8][log[:, 8] <= 0].sum()), 2)
    all_gross_loss_per = round(
        all_gross_loss / initial_capital * 100, 2
    )

    long_gross_loss = round(
        abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 0)].sum()), 2
    )
    long_gross_loss_per = round(
        long_gross_loss / initial_capital * 100, 2
    )

    short_gross_loss = round(
        abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 1)].sum()), 2
    )
    short_gross_loss_per = round(
        short_gross_loss / initial_capital * 100, 2
    )

    # Net profit
    all_net_profit = round(all_gross_profit - all_gross_loss, 2)
    all_net_profit_per = round(
        all_net_profit / initial_capital * 100, 2
    )

    long_net_profit = round(long_gross_profit - long_gross_loss, 2)
    long_net_profit_per = round(
        long_net_profit / initial_capital * 100, 2
    )

    short_net_profit = round(short_gross_profit - short_gross_loss, 2)
    short_net_profit_per = round(
        short_net_profit / initial_capital * 100, 2
    )

    # Profit factor
    if all_gross_loss != 0:
        all_profit_factor = round(
            all_gross_profit / all_gross_loss, 3
        )
    else:
        all_profit_factor = np.nan

    if long_gross_loss != 0:
        long_profit_factor =  round(
            long_gross_profit / long_gross_loss, 3
        )
    else:
        long_profit_factor = np.nan

    if short_gross_loss != 0:
        short_profit_factor = round(
            short_gross_profit / short_gross_loss, 3
        )
    else:
        short_profit_factor = np.nan

    # Commission paid
    all_commission_paid = round(log[:, 12].sum(), 2)
    long_commission_paid = round(log[:, 12][log[:, 0] == 0].sum(), 2)
    short_commission_paid = round(log[:, 12][log[:, 0] == 1].sum(), 2)

    # Total closed trades
    all_total_closed_trades = log.shape[0]
    long_total_closed_trades = log[log[:, 0] == 0].shape[0]
    short_total_closed_trades = log[log[:, 0] == 1].shape[0]

    # Number winning trades
    all_number_winning_trades = log[log[:, 8] > 0].shape[0]
    long_number_winning_trades = log[
        (log[:, 8] > 0) & (log[:, 0] == 0)
    ].shape[0]
    short_number_winning_trades = log[
        (log[:, 8] > 0) & (log[:, 0] == 1)
    ].shape[0]

    # Number losing trades
    all_number_losing_trades = log[log[:, 8] <= 0].shape[0]
    long_number_losing_trades = log[
        (log[:, 8] <= 0) & (log[:, 0] == 0)
    ].shape[0]
    short_number_losing_trades = log[
        (log[:, 8] <= 0) & (log[:, 0] == 1)
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
    all_avg_trade = round(log[:, 8].mean(), 2)
    all_avg_trade_per = round(log[:, 9].mean(), 2)

    long_avg_trade = round(log[:, 8][log[:, 0] == 0].mean(), 2)
    long_avg_trade_per = round(log[:, 9][log[:, 0] == 0].mean(), 2)

    short_avg_trade = round(log[:, 8][log[:, 0] == 1].mean(), 2)
    short_avg_trade_per = round(log[:, 9][log[:, 0] == 1].mean(), 2)

    # Avg winning trade
    all_avg_winning_trade = round(log[:, 8][log[:, 8] > 0].mean(), 2)
    all_avg_winning_trade_per = round(
        log[:, 9][log[:, 9] > 0].mean(), 2
    )

    long_avg_winning_trade = round(
        log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 0)].mean(), 2
    )
    long_avg_winning_trade_per = round(
        log[:, 9][(log[:, 9] > 0) & (log[:, 0] == 0)].mean(), 2
    )

    short_avg_winning_trade = round(
        log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 1)].mean(), 2
    )
    short_avg_winning_trade_per = round(
        log[:, 9][(log[:, 9] > 0) & (log[:, 0] == 1)].mean(), 2
    )

    # Avg losing trade
    all_avg_losing_trade = round(
        abs(log[:, 8][log[:, 8] <= 0].mean()), 2
    )
    all_avg_losing_trade_per = round(
        abs(log[:, 9][log[:, 9] <= 0].mean()), 2
    )

    long_avg_losing_trade = round(
        abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 0)].mean()), 2
    )
    long_avg_losing_trade_per = round(
        abs(log[:, 9][(log[:, 9] <= 0) & (log[:, 0] == 0)].mean()), 2
    )

    short_avg_losing_trade = round(
        abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 1)].mean()), 2
    )
    short_avg_losing_trade_per = round(
        abs(log[:, 9][(log[:, 9] <= 0) & (log[:, 0] == 1)].mean()), 2
    )

    # Ratio avg win / avg loss
    all_ratio_avg_win_loss = round(
        all_avg_winning_trade / all_avg_losing_trade, 3
    )
    long_ratio_avg_win_loss = round(
        long_avg_winning_trade / long_avg_losing_trade, 3
    )
    short_ratio_avg_win_loss = round(
        short_avg_winning_trade / short_avg_losing_trade, 3
    )

    # Largest winning trade
    all_largest_winning_trade = np.nan
    all_largest_winning_trade_per = np.nan

    try:
        all_largest_winning_trade = round(log[:, 8].max(), 2)
        all_largest_winning_trade_per = round(log[:, 9].max(), 2)
    except Exception:
        pass

    long_largest_winning_trade = np.nan
    long_largest_winning_trade_per = np.nan

    try:
        long_largest_winning_trade = round(
            log[:, 8][log[:, 0] == 0].max(), 2
        )
        long_largest_winning_trade_per = round(
            log[:, 9][log[:, 0] == 0].max(), 2
        )
    except Exception:
        pass

    short_largest_winning_trade = np.nan
    short_largest_winning_trade_per = np.nan

    try:
        short_largest_winning_trade = round(
            log[:, 8][log[:, 0] == 1].max(), 2
        )
        short_largest_winning_trade_per = round(
            log[:, 9][log[:, 0] == 1].max(), 2
        )
    except Exception:
        pass

    # Largest losing trade
    all_largest_losing_trade = np.nan
    all_largest_losing_trade_per = np.nan

    try:
        all_largest_losing_trade = round(abs(log[:, 8].min()), 2)
        all_largest_losing_trade_per = round(abs(log[:, 9].min()), 2)
    except Exception:
        pass

    long_largest_losing_trade = np.nan
    long_largest_losing_trade_per = np.nan  

    try:
        long_largest_losing_trade = round(
            abs(log[:, 8][log[:, 0] == 0].min()), 2
        )
        long_largest_losing_trade_per = round(
            abs(log[:, 9][log[:, 0] == 0].min()), 2
        )
    except Exception:
        pass

    short_largest_losing_trade = np.nan
    short_largest_losing_trade_per = np.nan

    try:
        short_largest_losing_trade = round(
            abs(log[:, 8][log[:, 0] == 1].min()), 2
        )
        short_largest_losing_trade_per = round(
            abs(log[:, 9][log[:, 0] == 1].min()), 2
        )
    except Exception:
        pass

    # Max drawdown
    try:
        equity = np.concatenate(
            (np.array([initial_capital]), log[:, 8])
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
    all_sortino_ratio = round(
        all_avg_trade_per / 
            (log[:, 9][log[:, 9] <= 0] ** 2).mean() ** 0.5,
        3
    )

    metrics = [
        [
            all_net_profit,
            all_net_profit_per,
            all_gross_profit,
            all_gross_profit_per,
            all_gross_loss,
            all_gross_loss_per,
            "" if np.isnan(all_profit_factor)
                else all_profit_factor,
            all_commission_paid,
            all_total_closed_trades,
            all_number_winning_trades,
            all_number_losing_trades,
            "" if np.isnan(all_percent_profitable)
                else all_percent_profitable,
            "" if np.isnan(all_avg_trade)
                else all_avg_trade,
            "" if np.isnan(all_avg_trade_per)
                else all_avg_trade_per,
            "" if np.isnan(all_avg_winning_trade)
                else all_avg_winning_trade,
            "" if np.isnan(all_avg_winning_trade_per)
                else all_avg_winning_trade_per,
            "" if np.isnan(all_avg_losing_trade)
                else all_avg_losing_trade,
            "" if np.isnan(all_avg_losing_trade_per)
                else all_avg_losing_trade_per,
            "" if np.isnan(all_ratio_avg_win_loss)
                else all_ratio_avg_win_loss,
            "" if np.isnan(all_largest_winning_trade)
                else all_largest_winning_trade,
            "" if np.isnan(all_largest_winning_trade_per)
                else all_largest_winning_trade_per,
            "" if np.isnan(all_largest_losing_trade)
                else all_largest_losing_trade,
            "" if np.isnan(all_largest_losing_trade_per)
                else all_largest_losing_trade_per,
            "" if np.isnan(all_max_drawdown)
                else all_max_drawdown,
            "" if np.isnan(all_max_drawdown_per)
                else all_max_drawdown_per,
            "" if np.isnan(all_sortino_ratio)
                else all_sortino_ratio
        ],
        [
            long_net_profit,
            long_net_profit_per,
            long_gross_profit,
            long_gross_profit_per,
            long_gross_loss,
            long_gross_loss_per,
            "" if np.isnan(long_profit_factor)
                else long_profit_factor,
            long_commission_paid,
            long_total_closed_trades,
            long_number_winning_trades,
            long_number_losing_trades,
            "" if np.isnan(long_percent_profitable)
                else long_percent_profitable,
            "" if np.isnan(long_avg_trade)
                else long_avg_trade,
            "" if np.isnan(long_avg_trade_per)
                else long_avg_trade_per,
            "" if np.isnan(long_avg_winning_trade)
                else long_avg_winning_trade,
            "" if np.isnan(long_avg_winning_trade_per)
                else long_avg_winning_trade_per,
            "" if np.isnan(long_avg_losing_trade)
                else long_avg_losing_trade,
            "" if np.isnan(long_avg_losing_trade_per)
                else long_avg_losing_trade_per,
            "" if np.isnan(long_ratio_avg_win_loss)
                else long_ratio_avg_win_loss,
            "" if np.isnan(long_largest_winning_trade)
                else long_largest_winning_trade,
            "" if np.isnan(long_largest_winning_trade_per)
                else long_largest_winning_trade_per,
            "" if np.isnan(long_largest_losing_trade)
                else long_largest_losing_trade,
            "" if np.isnan(long_largest_losing_trade_per)
                else long_largest_losing_trade_per
        ],
        [
            short_net_profit,
            short_net_profit_per,
            short_gross_profit,
            short_gross_profit_per,
            short_gross_loss,
            short_gross_loss_per,
            "" if np.isnan(short_profit_factor)
                else short_profit_factor,
            short_commission_paid,
            short_total_closed_trades,
            short_number_winning_trades,
            short_number_losing_trades,
            "" if np.isnan(short_percent_profitable)
                else short_percent_profitable,
            "" if np.isnan(short_avg_trade)
                else short_avg_trade,
            "" if np.isnan(short_avg_trade_per)
                else short_avg_trade_per,
            "" if np.isnan(short_avg_winning_trade)
                else short_avg_winning_trade,
            "" if np.isnan(short_avg_winning_trade_per)
                else short_avg_winning_trade_per,
            "" if np.isnan(short_avg_losing_trade)
                else short_avg_losing_trade,
            "" if np.isnan(short_avg_losing_trade_per)
                else short_avg_losing_trade_per,
            "" if np.isnan(short_ratio_avg_win_loss)
                else short_ratio_avg_win_loss,
            "" if np.isnan(short_largest_winning_trade)
                else short_largest_winning_trade,
            "" if np.isnan(short_largest_winning_trade_per)
                else short_largest_winning_trade_per,
            "" if np.isnan(short_largest_losing_trade)
                else short_largest_losing_trade,
            "" if np.isnan(short_largest_losing_trade_per)
                else short_largest_losing_trade_per
        ]
    ]

    return equity, metrics