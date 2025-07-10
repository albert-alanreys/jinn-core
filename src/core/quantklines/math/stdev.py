import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def stdev(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate rolling standard deviation over a specified window length.

    Args:
        source (np.ndarray): Input series (leading NaNs are skipped).
        length (int): Window size for standard deviation calculation.

    Returns:
        np.ndarray: Array of standard deviation values.
    """

    n = source.shape[0]
    result = np.full(n, np.nan, dtype=np.float64)

    for i in range(length - 1, n):
        sum_ = 0.0
        sum_sq = 0.0
        count = 0

        for j in range(i - length + 1, i + 1):
            val = source[j]

            if not np.isnan(val):
                sum_ += val
                sum_sq += val * val
                count += 1
            else:
                count = -1

        if count == length:
            mean = sum_ / length
            var = (sum_sq / length) - (mean * mean)
            result[i] = np.sqrt(var) if var > 0 else 0.0
        else:
            result[i] = np.nan

    return result