import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](
        nb.float64[:], nb.float64[:], nb.float64[:], nb.boolean
    ),
    cache=True,
    nogil=True
)
def tr(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    handle_nan: np.bool_
) -> np.ndarray:
    """
    Calculate True Range (TR) values from price series.

    Args:
        high (np.ndarray): High price series.
        low (np.ndarray): Low price series.
        close (np.ndarray): Close price series.
        handle_nan (bool): If True, computes first bar TR using current close,
                           if False, returns NaN for first bar.

    Returns:
        np.ndarray: True Range values array, NaN where invalid.
    """

    n = high.shape[0]
    result = np.full(n, np.nan, dtype=np.float64)

    for i in range(n):
        hl = high[i] - low[i]

        if i == 0:
            if handle_nan:
                hc = abs(high[i] - close[i])
                lc = abs(low[i] - close[i])
            else:
                result[i] = np.nan
                continue
        else:
            hc = abs(high[i] - close[i - 1])
            lc = abs(low[i] - close[i - 1])

        result[i] = max(hl, hc, lc)

    return result