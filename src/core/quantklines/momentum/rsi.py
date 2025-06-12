import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def rsi(source: np.ndarray, length: np.int16) -> np.ndarray:
    u = source - np.concatenate((np.full(1, np.nan), source[: -1]))
    d = np.concatenate((np.full(1, np.nan), source[: -1])) - source
    u[u < 0] = 0
    d[d < 0] = 0

    # rma_u
    rma_u = u.copy()
    alpha = 1 / length
    na_sum = np.isnan(rma_u).sum()
    rma_u[: length + na_sum - 1] = np.nan
    rma_u[length + na_sum - 1] = u[na_sum : length + na_sum].mean()

    for i in range(length + na_sum, rma_u.shape[0]):
        rma_u[i] = alpha * rma_u[i] + (1 - alpha) * rma_u[i - 1]

    # rma_d
    rma_d = d.copy()
    alpha = 1 / length
    na_sum = np.isnan(rma_d).sum()
    rma_d[: length + na_sum - 1] = np.nan
    rma_d[length + na_sum - 1] = d[na_sum : length + na_sum].mean()

    for i in range(length + na_sum, rma_d.shape[0]):
        rma_d[i] = alpha * rma_d[i] + (1 - alpha) * rma_d[i - 1]

    # values
    rs = rma_u / rma_d
    values = 100 - 100 / (1 + rs)
    return values