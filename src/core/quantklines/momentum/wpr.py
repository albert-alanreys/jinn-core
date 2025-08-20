import numpy as np
import numba as nb

from src.core.quantklines.utils import highest, lowest


@nb.njit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.int16),
    cache=True,
    nogil=True
)
def wpr(
    close: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    length: np.int16
) -> np.ndarray:
    """
    Calculate Williams Percent Range (WPR) indicator values.

    The function computes the percentage of current closing price relative to
    the high-low range over the specified period (-100 to 0 scale).

    Args:
        close: Closing price series
        settings: High price series
        low: Low price series
        length: Lookback period for high/low calculation

    Returns:
        np.ndarray: WPR values (-100 to 0), NaN where invalid
    """

    n = close.shape[0]
    result = np.full(n, np.nan, dtype=np.float64)

    highest_values = highest(high, length)
    lowest_values = lowest(low, length)

    for i in range(n):
        hi = highest_values[i]
        lo = lowest_values[i]
        cl = close[i]

        if np.isnan(hi) or np.isnan(lo) or np.isnan(cl):
            continue

        denom = hi - lo

        if denom == 0:
            result[i] = 0.0
        else:
            r = -100.0 * (hi - cl) / denom

            if r < -100.0:
                r = -100.0
            elif r > 0.0:
                r = 0.0

            result[i] = r

    return result