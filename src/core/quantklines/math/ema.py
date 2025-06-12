import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def ema(source: np.ndarray, length: np.int16) -> np.ndarray:
    values = source.copy()
    alpha = 2 / (length + 1)
    na_sum = np.isnan(values).sum()
    values[: length + na_sum - 1] = np.nan
    values[length + na_sum - 1] = source[na_sum : length + na_sum].mean()

    for i in range(length + na_sum, values.shape[0]):
        values[i] = alpha * values[i] + (1 - alpha) * values[i - 1]

    return values