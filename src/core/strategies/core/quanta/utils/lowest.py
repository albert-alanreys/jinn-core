from __future__ import annotations

import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def lowest(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate the lowest value over a sliding window.

    The function computes the minimum value for each position in the array
    looking back over the specified number of periods.

    Args:
        source: Input series (leading NaNs are skipped)
        length: Lookback window length

    Returns:
        np.ndarray: Array of lowest values
    """

    n = source.shape[0]
    result = np.empty(n, dtype=np.float64)

    for i in range(n):
        if i < length - 1:
            result[i] = np.nan
        else:
            min_val = np.inf
            has_valid = False

            for j in range(i - length + 1, i + 1):
                val = source[j]

                if not np.isnan(val):
                    has_valid = True

                    if val < min_val:
                        min_val = val

            result[i] = min_val if has_valid else np.nan

    return result