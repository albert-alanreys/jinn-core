import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](
        nb.float64[:],
        nb.float64[:],
        nb.float64[:],
        nb.float64[:],
        nb.float64[:]
    ),
    cache=True, nopython=True, nogil=True
)
def vwap(
    time: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> np.ndarray:
    values = np.empty(time.shape[0], dtype=np.float64)
    price = (high + low + close) / 3.0

    cum_vol = 0.0
    cum_vol_price = 0.0
    prev_day = time[0] // 86400000

    for i in range(time.shape[0]):
        current_day = time[i] // 86400000

        if current_day != prev_day:
            cum_vol = 0.0
            cum_vol_price = 0.0
            prev_day = current_day

        cum_vol += volume[i]
        cum_vol_price += price[i] * volume[i]
        values[i] = cum_vol_price / cum_vol

    return values