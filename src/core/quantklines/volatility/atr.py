import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def atr(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    length: np.int16
) -> np.ndarray:
    # tr
    hl = high - low
    hc = np.absolute(
        high - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    lc = np.absolute(
        low - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    hc[0] = abs(high[0] - close[0])
    lc[0] = abs(low[0] - close[0])
    tr = np.maximum(np.maximum(hl, hc), lc)

    # values
    alpha = 1 / length
    values = tr.copy()
    na_sum = np.isnan(values).sum()
    values[length + na_sum - 1] = tr[na_sum : length + na_sum].mean()
    values[: length + na_sum - 1] = np.nan

    for i in range(length + na_sum, values.shape[0]):
        values[i] = alpha * values[i] + (1 - alpha) * values[i - 1]

    return values