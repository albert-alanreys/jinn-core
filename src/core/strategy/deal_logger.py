import numpy as np
import numba as nb


@nb.njit(
    nb.types.Tuple((nb.float64[:, :], nb.float64))(
        nb.float64[:, :],
        nb.float64, nb.float64, nb.float64,
        nb.float64, nb.float64, nb.float64,
        nb.float64, nb.float64, nb.float64,
        nb.float64
    ),
    cache=True,
    nogil=True
)
def update_completed_deals_log(
    completed_deals_log: np.ndarray,
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
) -> tuple:
    """
    Creates and appends a new deal record to completed deals log.
    Returns updated log and calculated PnL.

    Args:
        completed_deals_log: Existing log array [n,13] or empty [0,13]
        commission (float64): Broker commission rate in percent
        deal_type (float64): Type of deal (0 for long, 1 for short)
        entry_signal (float64): Signal value at entry
        exit_signal (float64): Signal value at exit
        entry_date (float64): Timestamp of entry
        exit_date (float64): Timestamp of exit
        entry_price (float64): Price at entry
        exit_price (float64): Price at exit
        position_size (float64): Size of the position
        initial_capital (float64): Initial capital for PnL calculations

    Returns:
        tuple: (updated_log, pnl) where:
            updated_log: New log array [n+1,13] with fields:
                [:, 0] - deal_type (0=long, 1=short)
                [:, 1] - entry_signal (signal code)
                [:, 2] - exit_signal (signal code)
                [:, 3] - entry_date (timestamp)
                [:, 4] - exit_date (timestamp)
                [:, 5] - entry_price (USDT)
                [:, 6] - exit_price (USDT)
                [:, 7] - position_size (units)
                [:, 8] - pnl (absolute USDT)
                [:, 9] - pnl (percentage)
                [:,10] - cumulative_pnl (USDT)
                [:,11] - cumulative_pnl (%)
                [:,12] - total_commission (USDT)
            pnl: Calculated profit/loss for this deal in USDT

    Notes:
        For empty position_size returns original log and 0 pnl.
        Automatically handles empty input log case.
        All monetary values rounded to 2 decimal places.
    """

    total_commission = round(
        (position_size * entry_price * commission / 100.0) +
        (position_size * exit_price * commission / 100.0),
        2
    )

    if position_size == 0.0:
        return completed_deals_log, 0.0

    if deal_type == 0.0:
        pnl = round(
            (exit_price - entry_price) * position_size - total_commission,
            2
        )
    else:
        pnl = round(
            (entry_price - exit_price) * position_size - total_commission,
            2
        )

    pnl_per = round(
        (((position_size * entry_price) + pnl) /
        (position_size * entry_price) - 1.0) * 100.0,
        2
    )


    if completed_deals_log.shape[0] == 0:
        cum_pnl = round(pnl, 2)
        cum_pnl_per = round(pnl / (initial_capital + pnl) * 100.0, 2)
    else:
        cum_pnl = round(pnl + completed_deals_log[-1, 10], 2)
        cum_pnl_per = round(
            pnl / (initial_capital + completed_deals_log[-1, 10]) * 100.0,
            2
        )

    log_entry = np.empty(13, dtype=np.float64)
    log_entry[0] = deal_type
    log_entry[1] = entry_signal
    log_entry[2] = exit_signal
    log_entry[3] = entry_date
    log_entry[4] = exit_date
    log_entry[5] = entry_price
    log_entry[6] = exit_price
    log_entry[7] = position_size
    log_entry[8] = pnl
    log_entry[9] = pnl_per
    log_entry[10] = cum_pnl
    log_entry[11] = cum_pnl_per
    log_entry[12] = total_commission

    if completed_deals_log.shape[0] == 0:
        updated_log = log_entry.reshape(1, -1)
    else:
        updated_log = np.empty(
            (completed_deals_log.shape[0] + 1, 13),
            dtype=np.float64
        )
        updated_log[:-1] = completed_deals_log
        updated_log[-1] = log_entry

    return updated_log, pnl