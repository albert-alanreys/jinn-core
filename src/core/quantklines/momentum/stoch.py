import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def stoch(
    source: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    length: np.int16
) -> np.ndarray:
    # highest
    high = high.copy()
    high[np.isnan(high)] = -np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(high, length)
    highest = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        highest[i] = rolling[i].max()

    highest = np.concatenate((np.full(length - 1, np.nan), highest))
    highest[highest == -np.inf] = np.nan

    # lowest
    low = low.copy()
    low[np.isnan(low)] = np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(low, length)
    lowest = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        lowest[i] = rolling[i].min()

    lowest = np.concatenate((np.full(length - 1, np.nan), lowest))
    lowest[lowest == np.inf] = np.nan

    # values
    values = 100 * (source - lowest) / (highest - lowest)
    values = np.where(values > 100, 100, values)
    values = np.where(values < 0, 0, values)

    return values