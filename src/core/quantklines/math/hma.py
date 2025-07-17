import numpy as np
import numba as nb

from .wma import wma


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def hma(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate HMA (Hull Moving Average).

    The HMA is calculated in three steps:
    1. Compute WMA of the source with half the given length (length // 2).
    2. Compute WMA of the source with the full given length.
    3. Compute a raw HMA as: 2 * WMA(half_length) - WMA(full_length).
    4. Apply WMA to the raw HMA with period sqrt(length) to get the final HMA.

    Args:
        source (np.ndarray): Input series (leading NaNs are skipped)
        length (int): HMA period length

    Returns:
        np.ndarray: HMA values array
    """

    n = source.shape[0]
    wma_half = wma(source, length // 2)
    wma_full = wma(source, length)

    # raw_hma = 2 * wma_half - wma_full
    raw_hma = np.full(n, np.nan, dtype=np.float64)
    for i in range(n):
        val1 = wma_half[i]
        val2 = wma_full[i]

        if not np.isnan(val1) and not np.isnan(val2):
            raw_hma[i] = 2.0 * val1 - val2

    hma_length = int(length ** 0.5)
    weight_sum = hma_length * (hma_length + 1) / 2.0
    result = np.full(n, np.nan, dtype=np.float64)

    for i in range(hma_length - 1, n):
        weighted_sum = 0.0
        valid = True
        for j in range(hma_length):
            val = raw_hma[i - hma_length + 1 + j]

            if np.isnan(val):
                valid = False
                break

            weighted_sum += val * (j + 1)

        if valid:
            result[i] = weighted_sum / weight_sum

    return result