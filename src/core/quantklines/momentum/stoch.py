import numpy as np
import numba as nb

from src.core.quantklines.utils import highest, lowest


@nb.njit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.int16),
    cache=True,
    nogil=True
)
def stoch(
    source: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    length: np.int16
) -> np.ndarray:
    """
    Calculate stochastic oscillator values for the input series.

    The function computes the percentage of current closing price relative to
    the high-low range over the specified period (0-100 scale).

    Args:
        source (np.ndarray): Closing price series.
        high (np.ndarray): High price series.
        low (np.ndarray): Low price series.
        length (int): Lookback period for high/low calculation.

    Returns:
        np.ndarray: Stochastic oscillator values (0-100), NaN where invalid.
    """

    n = source.shape[0]
    result = np.full(n, np.nan, dtype=np.float64)

    highest_values = highest(high, length)
    lowest_values = lowest(low, length)

    for i in range(n):
        hi = highest_values[i]
        lo = lowest_values[i]
        val = source[i]

        if np.isnan(hi) or np.isnan(lo) or np.isnan(val):
            continue

        denom = hi - lo

        if denom == 0:
            result[i] = 0.0
        else:
            r = 100.0 * (val - lo) / denom

            if r > 100.0:
                r = 100.0
            elif r < 0.0:
                r = 0.0

            result[i] = r

    return result