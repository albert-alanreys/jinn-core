import numpy as np
import numba as nb


@nb.jit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.int16, nb.float32
    ), 
    cache=True, nopython=True, nogil=True
)
def bb(
    source: np.ndarray,
    length: np.int16,
    mult: np.float32
) -> np.ndarray:
    # sma
    rolling = np.lib.stride_tricks.sliding_window_view(source, length)
    sma = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        sma[i] = rolling[i].mean()

    sma = np.concatenate((np.full(length - 1, np.nan), sma))

    # stdev
    rolling = np.lib.stride_tricks.sliding_window_view(source, length)
    stdev = np.full(rolling.shape[0], np.nan)

    for i in range(rolling.shape[0]):
        stdev[i] = rolling[i].std()

    stdev = np.concatenate((np.full(length - 1, np.nan), stdev))

    # values
    upper = sma + mult * stdev
    lower = sma - mult * stdev
    values = (sma, upper, lower)
    return values