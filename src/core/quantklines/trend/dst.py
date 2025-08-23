from __future__ import annotations

import numpy as np
import numba as nb

from src.core.quantklines.volatility import atr


@nb.njit(
    nb.types.Tuple((nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.float64[:], nb.float32, nb.int16
    ),
    cache=True,
    nogil=True
)
def dst(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    factor: np.float32,
    atr_length: np.int16
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate Double SuperTrend (DST) indicator bands.

    The function computes two persistent bands (upper and lower)
    based on ATR-adjusted midpoints of high-low prices.
    Unlike standard SuperTrend, maintains both bands.

    Args:
        settings: High price series
        low: Low price series
        close: Close price series
        factor: Multiplier for ATR band width
        atr_length: Period length for ATR calculation

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - First array: Upper band values
            - Second array: Lower band values
    """

    n = high.shape[0]
    atr_values = atr(high, low, close, atr_length)
    
    hl2 = 0.5 * (high + low)
    upper_band = hl2 + factor * atr_values
    lower_band = hl2 - factor * atr_values

    for i in range(1, n):
        if np.isnan(atr_values[i]) or np.isnan(atr_values[i - 1]):
            continue

        if (
            upper_band[i] >= upper_band[i - 1] and
            close[i - 1] <= upper_band[i - 1]
        ):
            upper_band[i] = upper_band[i - 1]

        if (
            lower_band[i] <= lower_band[i - 1] and
            close[i - 1] >= lower_band[i - 1]
        ):
            lower_band[i] = lower_band[i - 1]

    return upper_band, lower_band