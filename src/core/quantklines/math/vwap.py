import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](
        nb.float64[:],
        nb.float64[:],
        nb.float64[:],
        nb.float64[:],
        nb.float64[:]
    ),
    cache=True, nogil=True
)
def vwap(time: np.ndarray,
         high: np.ndarray,
         low: np.ndarray,
         close: np.ndarray,
         volume: np.ndarray) -> np.ndarray:
    """
    Calculate VWAP (Volume-Weighted Average Price) on a daily basis.

    The VWAP is computed as cumulative typical price multiplied by volume,
    divided by cumulative volume, resetting at each new trading day.
    Typical price is calculated as (high + low + close) / 3 for each period.

    Args:
        time (np.ndarray): Timestamps in milliseconds
        high (np.ndarray): High prices for each period
        low (np.ndarray): Low prices for each period
        close (np.ndarray): Close prices for each period
        volume (np.ndarray): Trading volume for each period

    Returns:
        np.ndarray: VWAP values array
    """

    n = time.shape[0]
    result = np.empty(n, dtype=np.float64)

    typical_price = (high + low + close) / 3.0
    cum_volume = 0.0
    cum_volume_price = 0.0
    prev_day = int(time[0] // 86400000)

    for i in range(n):
        current_day = int(time[i] // 86400000)

        if current_day != prev_day:
            cum_volume = 0.0
            cum_volume_price = 0.0
            prev_day = current_day

        vol = volume[i]
        price = typical_price[i]

        cum_volume += vol
        cum_volume_price += price * vol
        result[i] = cum_volume_price / cum_volume

    return result