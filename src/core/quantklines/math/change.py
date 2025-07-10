import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def change(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate the difference between current values
    and past values in a data series.

    Args:
        source (np.ndarray): Input data series.
        length (np.int16): Number of periods to look back 
                           or calculating the difference.

    Returns:
        np.ndarray: Array with the computed differences,
                    where the first `length` elements are NaN.
    """

    n = source.shape[0]
    result = np.empty(n, dtype=np.float64)

    for i in range(length):
        result[i] = np.nan

    for i in range(length, n):
        result[i] = source[i] - source[i - length]

    return result