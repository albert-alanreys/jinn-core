import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def wpr(
    source1: np.ndarray,
    source2: np.ndarray,
    source3: np.ndarray,
    length: np.int16
) -> np.ndarray:
    # highest
    source1 = source1.copy()
    source1[np.isnan(source1)] = -np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(source1, length)
    highest = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        highest[i] = rolling[i].max()

    highest = np.concatenate((np.full(length - 1, np.nan), highest))
    highest[highest == -np.inf] = np.nan

    # lowest
    source2 = source2.copy()
    source2[np.isnan(source2)] = np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(source2, length)
    lowest = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        lowest[i] = rolling[i].min()

    lowest = np.concatenate((np.full(length - 1, np.nan), lowest))
    lowest[lowest == np.inf] = np.nan

    # values
    values = 100 * (source3 - highest) / (highest - lowest)
    return values