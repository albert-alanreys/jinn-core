import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16, nb.int16), 
    cache=True, nopython=True, nogil=True
)
def pivothigh(
    source: np.ndarray,
    leftbars: np.int16,
    rightbars: np.int16
) -> np.ndarray:
    source = source.copy()
    source[np.isnan(source)] = -np.inf
    length = leftbars + rightbars + 1
    rolling = np.lib.stride_tricks.sliding_window_view(source, length)
    values = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        values[i] = rolling[i].max()

    values = np.concatenate((np.full(length - 1, np.nan), values))
    values[values == -np.inf] = np.nan
    values[
        values != np.concatenate(
            (np.full(rightbars, np.nan), source[: -rightbars])
        )
    ] = np.nan
    return values