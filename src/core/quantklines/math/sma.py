import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def sma(source: np.ndarray, length: np.int16) -> np.ndarray:
    rolling = np.lib.stride_tricks.sliding_window_view(source, length)
    values = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        values[i] = rolling[i].mean()

    values = np.concatenate((np.full(length - 1, np.nan), values))
    return values