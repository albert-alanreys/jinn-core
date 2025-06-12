import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def hma(source: np.ndarray, length: np.int16) -> np.ndarray:
    # wma1
    wma1_length = length // 2
    rolling = np.lib.stride_tricks.sliding_window_view(source, wma1_length)
    wma1 = np.full(rolling.shape[0], np.nan)
    weights = np.full(wma1_length, np.nan)

    for i in range(weights.shape[0]):
        weights[i] = 2 / (wma1_length * (wma1_length + 1)) * (wma1_length - i)

    weights = weights[::-1]

    for i in range(rolling.shape[0]):
        wma1[i] = (rolling[i] * weights).sum()

    wma1 = np.concatenate((np.full(wma1_length - 1, np.nan), wma1))
    
    # wma2
    wma2_length = length
    rolling = np.lib.stride_tricks.sliding_window_view(source, wma2_length)
    wma2 = np.full(rolling.shape[0], np.nan)
    weights = np.full(wma2_length, np.nan)

    for i in range(weights.shape[0]):
        weights[i] = 2 / (wma2_length * (wma2_length + 1)) * (wma2_length - i)

    weights = weights[::-1]

    for i in range(rolling.shape[0]):
        wma2[i] = (rolling[i] * weights).sum()

    wma2 = np.concatenate((np.full(wma2_length - 1, np.nan), wma2))

    # raw_hma
    raw_hma = 2 * wma1 - wma2

    # values
    hma_length = int(length ** 0.5)
    rolling = np.lib.stride_tricks.sliding_window_view(raw_hma, hma_length)
    values = np.full(rolling.shape[0], np.nan)
    weights = np.full(hma_length, np.nan)

    for i in range(weights.shape[0]):
        weights[i] = 2 / (hma_length * (hma_length + 1)) * (hma_length - i)

    weights = weights[::-1]

    for i in range(rolling.shape[0]):
        values[i] = (rolling[i] * weights).sum()

    values = np.concatenate((np.full(hma_length - 1, np.nan), values))
    return values