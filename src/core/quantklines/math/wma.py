import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def wma(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate WMA (Weighted Moving Average) with linear weights.

    Args:
        source: Input series (leading NaNs are skipped)
        length: WMA period length

    Returns:
        np.ndarray: WMA values array
    """

    n = source.shape[0]
    result = np.empty(n, dtype=np.float64)
    weight_sum = length * (length + 1) / 2.0

    for i in range(n):
        if i < length - 1 or np.isnan(source[i]):
            result[i] = np.nan
            continue

        weighted_sum = 0.0
        for j in range(length):
            weight = (j + 1)
            val = source[i - length + 1 + j]

            if np.isnan(val):
                weighted_sum = np.nan
                break

            weighted_sum += val * weight

        if not np.isnan(weighted_sum):
            result[i] = weighted_sum / weight_sum
        else:
            result[i] = np.nan

    return result