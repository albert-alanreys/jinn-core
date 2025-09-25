from __future__ import annotations

import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:, :](
        nb.float64[:, :],
        nb.float64,
        nb.float64,
        nb.float64,
        nb.float64,
        nb.float64
    ),
    cache=True,
    nogil=True
)
def open(
    open_deals_log: np.ndarray,
    position_type: float,
    order_signal: float,
    order_date: float,
    order_price: float,
    order_size: float
) -> np.ndarray:
    """
    Adds a new deal to the open deals log, expanding the array if necessary.
    
    Args:
        open_deals_log: Current open deals log array [n,5]
        position_type: Type of deal (0 for long, 1 for short)
        order_signal: Signal value at entry
        order_date: Timestamp of entry
        order_price: Price at entry
        order_size: Size of the order
        
    Returns:
        np.ndarray: Updated open deals log [n+1,5] with fields:
            [:, 0] - position_type (0=long, 1=short)
            [:, 1] - order_signal (signal code)
            [:, 2] - order_date (timestamp)
            [:, 3] - order_price (USDT)
            [:, 4] - order_size (units)
            
    Notes:
        - If input log is empty (all NaN), fills first available slot
        - If input log is full, expands array by one row
    """
    
    # Find first available slot (all NaN row)
    for i in range(open_deals_log.shape[0]):
        if np.isnan(open_deals_log[i, 0]):
            open_deals_log[i, 0] = position_type
            open_deals_log[i, 1] = order_signal
            open_deals_log[i, 2] = order_date
            open_deals_log[i, 3] = order_price
            open_deals_log[i, 4] = order_size
            return open_deals_log
    
    # If no free slots, expand the array
    new_log = np.empty(
        (open_deals_log.shape[0] + 1, 5),
        dtype=np.float64
    )
    
    # Copy existing deals
    new_log[:-1] = open_deals_log
    
    # Add new deal to the last row
    new_log[-1, 0] = position_type
    new_log[-1, 1] = order_signal
    new_log[-1, 2] = order_date
    new_log[-1, 3] = order_price
    new_log[-1, 4] = order_size
    
    return new_log


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
def close(
    completed_deals_log: np.ndarray,
    commission: float,
    position_type: float,
    order_signal: float,
    exit_signal: float,
    order_date: float,
    exit_date: float,
    order_price: float,
    exit_price: float,
    order_size: float,
    initial_capital: float
) -> tuple:
    """
    Creates and appends a new deal record to completed deals log.
    Returns updated log and calculated PnL.

    Args:
        completed_deals_log: Existing log array [n,13] or empty [0,13]
        commission (float64): Broker commission rate in percent
        position_type (float64): Type of deal (0 for long, 1 for short)
        order_signal (float64): Signal value at entry
        exit_signal (float64): Signal value at exit
        order_date (float64): Timestamp of entry
        exit_date (float64): Timestamp of exit
        order_price (float64): Price at entry
        exit_price (float64): Price at exit
        order_size (float64): Size of the order
        initial_capital (float64): Initial capital for PnL calculations

    Returns:
        tuple: (updated_log, pnl) where:
            updated_log: New log array [n+1,13] with fields:
                [:, 0] - position_type (0=long, 1=short)
                [:, 1] - order_signal (signal code)
                [:, 2] - exit_signal (signal code)
                [:, 3] - order_date (timestamp)
                [:, 4] - exit_date (timestamp)
                [:, 5] - order_price (USDT)
                [:, 6] - exit_price (USDT)
                [:, 7] - order_size (units)
                [:, 8] - pnl (absolute USDT)
                [:, 9] - pnl (percentage)
                [:,10] - cumulative_pnl (USDT)
                [:,11] - cumulative_pnl (%)
                [:,12] - total_commission (USDT)
            pnl: Calculated profit/loss for this deal in USDT

    Notes:
        - For empty order_size returns original log and 0 pnl
        - All monetary values rounded to 2 decimal places
    """

    total_commission = round(
        (order_size * order_price * commission / 100.0) +
        (order_size * exit_price * commission / 100.0),
        2
    )

    if order_size == 0.0:
        return completed_deals_log, 0.0

    if position_type == 0.0:
        pnl = round(
            (exit_price - order_price) * order_size - total_commission,
            2
        )
    else:
        pnl = round(
            (order_price - exit_price) * order_size - total_commission,
            2
        )

    pnl_per = round(
        (((order_size * order_price) + pnl) /
        (order_size * order_price) - 1.0) * 100.0,
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
    log_entry[0] = position_type
    log_entry[1] = order_signal
    log_entry[2] = exit_signal
    log_entry[3] = order_date
    log_entry[4] = exit_date
    log_entry[5] = order_price
    log_entry[6] = exit_price
    log_entry[7] = order_size
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


@nb.njit(
    nb.float64[:, :](nb.float64[:, :], nb.int64),
    cache=True,
    nogil=True
)
def remove(
    open_deals_log: np.ndarray,
    deal_index: int
) -> np.ndarray:
    """
    Removes a deal from open deals log by setting its row to NaN.
    
    Args:
        open_deals_log: Current open deals log array
        deal_index: Index of the deal to remove
        
    Returns:
        np.ndarray: Updated open deals log with specified deal removed
    """
    if 0 <= deal_index < open_deals_log.shape[0]:
        open_deals_log[deal_index, :] = np.nan
    
    return open_deals_log


@nb.njit(
    nb.float64[:, :](nb.float64[:, :], nb.int64, nb.float64),
    cache=True,
    nogil=True
)
def resize(
    open_deals_log: np.ndarray,
    deal_index: int,
    new_size: float
) -> np.ndarray:
    """
    Updates the position size for a specific deal in open deals log.
    
    Args:
        open_deals_log: Current open deals log array [n,5]
        deal_index: Index of the deal to resize
        new_size: New position size (units)
        
    Returns:
        np.ndarray: Updated open deals log with resized position
        
    Notes:
        - If deal_index is invalid or deal doesn't exist, returns original log
        - New size must be positive, otherwise sets to 0.0
        - If new size is 0.0, removes the deal from log
    """
    
    if (deal_index < 0 or deal_index >= open_deals_log.shape[0] or
        np.isnan(open_deals_log[deal_index, 0])):
        return open_deals_log
    
    if new_size <= 0.0:
        open_deals_log[deal_index, :] = np.nan
    else:
        open_deals_log[deal_index, 4] = new_size
    
    return open_deals_log


@nb.njit(nb.float64[:, :](nb.float64[:, :]), cache=True, nogil=True)
def clear(open_deals_log: np.ndarray) -> np.ndarray:
    """
    Clears all deals from open deals log by setting all values to NaN.
    
    Args:
        open_deals_log: Current open deals log array
        
    Returns:
        np.ndarray: Cleared open deals log (all NaN)
    """

    open_deals_log[:, :] = np.nan
    return open_deals_log


@nb.njit(nb.float64(nb.float64[:, :]), cache=True, nogil=True)
def avg_price(open_deals_log: np.ndarray) -> float:
    """
    Calculates the average entry price weighted by position size
    from open deals log.
    
    Args:
        open_deals_log: Open deals log array [n,5] with fields:
            [:, 0] - position_type (0=long, 1=short)
            [:, 1] - order_signal (signal code)
            [:, 2] - order_date (timestamp)
            [:, 3] - order_price (USDT)
            [:, 4] - order_size (units)
            
    Returns:
        float: Weighted average entry price, or NaN if no open deals
        
    Notes:
        - Only considers non-NaN deals (active positions)
        - Returns NaN if total size is 0 or no active deals found
        - Uses size-weighted average: sum(price * size) / sum(size)
    """

    total_size = 0.0
    weighted_price = 0.0
    
    for i in range(open_deals_log.shape[0]):
        if not np.isnan(open_deals_log[i, 0]):
            size = open_deals_log[i, 4]
            price = open_deals_log[i, 3]
            
            total_size += size
            weighted_price += price * size
    
    if total_size > 0.0:
        return weighted_price / total_size
    else:
        return np.nan


@nb.njit(nb.float64(nb.float64[:, :]), cache=True, nogil=True)
def size(open_deals_log: np.ndarray) -> float:
    """
    Calculates the total position size from open deals log.
    
    Args:
        open_deals_log: Open deals log array [n,5]
            
    Returns:
        float: Total position size across all open deals,
               or 0.0 if no open deals
        
    Notes:
        - Only considers non-NaN deals (active positions)
        - Returns 0.0 if no active deals found
    """

    total_size = 0.0
    
    for i in range(open_deals_log.shape[0]):
        if not np.isnan(open_deals_log[i, 0]):
            total_size += open_deals_log[i, 4]
    
    return total_size


@nb.njit(nb.int64(nb.float64[:, :]), cache=True, nogil=True)
def count(open_deals_log: np.ndarray) -> int:
    """
    Counts the number of active (non-NaN) deals in open deals log.
    
    Args:
        open_deals_log: Open deals log array [n,5]
            
    Returns:
        int: Number of active open deals
    """
    
    count = 0
    
    for i in range(open_deals_log.shape[0]):
        if not np.isnan(open_deals_log[i, 0]):
            count += 1
    
    return count