import numpy as np
import numba as nb


@nb.jit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.int16
    ), 
    cache=True, nopython=True, nogil=True
)
def donchian(
    source1: np.ndarray,
    source2: np.ndarray,
    length: np.int16
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # upper
    source1 = source1.copy()
    source1[np.isnan(source1)] = -np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(source1, length)
    upper = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        upper[i] = rolling[i].max()

    upper = np.concatenate((np.full(length - 1, np.nan), upper))
    upper[upper == -np.inf] = np.nan

    # lower
    source2 = source2.copy()
    source2[np.isnan(source2)] = np.inf
    rolling = np.lib.stride_tricks.sliding_window_view(source2, length)
    lower = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        lower[i] = rolling[i].min()

    lower = np.concatenate((np.full(length - 1, np.nan), lower))
    lower[lower == np.inf] = np.nan 

    # middle
    middle = (upper + lower) / 2

    # values
    values = (upper, lower, middle)
    return values