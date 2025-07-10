import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def sma(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate SMA (Simple Moving Average) of a data series.

    Args:
        source (np.ndarray): Input series (leading NaNs are skipped).
        length (int): SMA period length.

    Returns:
        np.ndarray: SMA values array.
    """

    n = source.shape[0]
    result = np.full(n, np.nan)

    if n < length:
        return result

    start = 0
    while start < n and np.isnan(source[start]):
        start += 1

    if n - start < length:
        return result

    window_sum = 0.0
    for i in range(start, start + length):
        if np.isnan(source[i]):
            return result

        window_sum += source[i]

    idx = start + length - 1
    result[idx] = window_sum / length

    for i in range(idx + 1, n):
        window_sum += source[i] - source[i - length]
        result[i] = window_sum / length

    return result