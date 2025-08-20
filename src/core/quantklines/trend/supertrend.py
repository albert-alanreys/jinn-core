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
def supertrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    factor: np.float32,
    atr_length: np.int16
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate SuperTrend indicator values and direction.

    The function computes the SuperTrend indicator using ATR-based bands
    around the midpoint of high-low prices. Tracks trend direction
    with band switches.

    Args:
        settings: High price series
        low: Low price series
        close: Close price series
        factor: Multiplier for ATR band width
        atr_length: Period length for ATR calculation

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - First array: SuperTrend indicator values
            - Second array: Direction (-1 for uptrend, 1 for downtrend)
    """

    n = high.shape[0]
    atr_values = atr(high, low, close, atr_length)
    
    hl2 = (high + low) * 0.5
    upper_band = hl2 + factor * atr_values
    lower_band = hl2 - factor * atr_values

    indicator = np.full(n, np.nan)
    direction = np.full(n, np.nan)

    for i in range(1, n):
        if np.isnan(atr_values[i]):
            continue

        if not np.isnan(indicator[i - 1]):
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

        if np.isnan(indicator[i - 1]):
            direction[i] = 1
            indicator[i] = upper_band[i]
        elif indicator[i - 1] == upper_band[i - 1]:
            if close[i] > upper_band[i]:
                direction[i] = -1
                indicator[i] = lower_band[i]
            else:
                direction[i] = 1
                indicator[i] = upper_band[i]
        else:
            if close[i] < lower_band[i]:
                direction[i] = 1
                indicator[i] = upper_band[i]
            else:
                direction[i] = -1
                indicator[i] = lower_band[i]

    return indicator, direction