import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](
        nb.float64[:], nb.float64, nb.float64, nb.float64,
        nb.float64, nb.float64, nb.float64, nb.float64,
        nb.float64, nb.float64, nb.float64
    ),
    cache=True,
    nogil=True
)
def create_log_entry(
    log: np.ndarray,
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
) -> np.ndarray:
    """
    Creates a log entry for a trading deal with calculated PnL metrics.

    Processes trading deal parameters to create a structured log entry with:
    - Deal type and signal information
    - Entry/exit dates and prices
    - Position size and commission
    - Calculated PnL (absolute and percentage)
    - Cumulative PnL (absolute and percentage)

    Args:
        log (float64[:]): Existing log array (empty for first entry).
        commission (float64): Broker commission rate in percent.
        deal_type (float64): Type of deal (0 for long, other for short).
        entry_signal (float64): Signal value at entry.
        exit_signal (float64): Signal value at exit.
        entry_date (float64): Timestamp of entry.
        exit_date (float64): Timestamp of exit.
        entry_price (float64): Price at entry.
        exit_price (float64): Price at exit.
        position_size (float64): Size of the position.
        initial_capital (float64): Initial capital for PnL calculations.

    Returns:
        float64[13]: Array containing structured log entry with fields:
            [0] - deal_type
            [1] - entry_signal
            [2] - exit_signal
            [3] - entry_date
            [4] - exit_date
            [5] - entry_price
            [6] - exit_price
            [7] - position_size
            [8] - pnl (absolute)
            [9] - pnl (percentage)
            [10] - cumulative_pnl (absolute)
            [11] - cumulative_pnl (percentage)
            [12] - total_commission

    Notes:
        - All monetary values are rounded to 2 decimal places.
        - Returns empty array if position_size is 0.
        - For first entry, cumulative PnL equals the current deal PnL.
        - For short deals (deal_type != 0), PnL calculation is inverted.
    """

    total_commission = round(
        (position_size * entry_price * commission / 100.0) +
        (position_size * exit_price * commission / 100.0),
        2
    )

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

    if position_size == 0.0:
        return np.empty(0, dtype=np.float64)

    pnl_per = round(
        (((position_size * entry_price) + pnl) /
        (position_size * entry_price) - 1.0) * 100.0,
        2
    )

    if log.shape[0] == 0:
        cum_pnl = round(pnl, 2)
        cum_pnl_per = round(pnl / (initial_capital + pnl) * 100.0, 2)
    else:
        cum_pnl = round(pnl + log[-3], 2)
        cum_pnl_per = round(pnl / (initial_capital + log[-3]) * 100.0, 2)

    result = np.empty(13, dtype=np.float64)
    result[0] = deal_type
    result[1] = entry_signal
    result[2] = exit_signal
    result[3] = entry_date
    result[4] = exit_date
    result[5] = entry_price
    result[6] = exit_price
    result[7] = position_size
    result[8] = pnl
    result[9] = pnl_per
    result[10] = cum_pnl
    result[11] = cum_pnl_per
    result[12] = total_commission

    return result