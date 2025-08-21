import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def rma(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate Wilder's RMA (Rolling Moving Average) used in RSI.

    The RMA is a special smoothing average where alpha = 1 / length.
    First value is simple moving average (SMA) of first 'length' periods.

    Args:
        source: Input series (leading NaNs are skipped)
        length: RMA period length

    Returns:
        np.ndarray: RMA values array
    """

    n = source.shape[0]
    alpha = 1 / length
    result = np.empty(n, dtype=np.float64)

    na_sum = 0
    for i in range(n):
        if np.isnan(source[i]):
            na_sum += 1
        else:
            break

    for i in range(length + na_sum - 1):
        result[i] = np.nan

    sum_ = 0.0
    for i in range(na_sum, na_sum + length):
        sum_ += source[i]

    start = length + na_sum - 1
    result[start] = sum_ / length

    for i in range(start + 1, n):
        result[i] = alpha * source[i] + (1 - alpha) * result[i - 1]

    return result