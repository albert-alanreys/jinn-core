import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def wma(source: np.ndarray, length: np.int16) -> np.ndarray:
    rolling = np.lib.stride_tricks.sliding_window_view(source, length)
    values = np.full(rolling.shape[0], np.nan)
    weights = np.full(length, np.nan)

    for i in range(weights.shape[0]):
        weights[i] = 2 / (length * (length + 1)) * (length - i)

    weights = weights[::-1]

    for i in range(rolling.shape[0]):
        values[i] = (rolling[i] * weights).sum()

    values = np.concatenate((np.full(length - 1, np.nan), values))
    return values