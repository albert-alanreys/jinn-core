import numpy as np
import numba as nb

from src.core.quantklines.math import rma
from src.core.quantklines.volatility import tr


@nb.njit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.float64[:], nb.int16, nb.int16
    ),
    cache=True, 
    nogil=True
)
def dmi(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    di_length: np.int16,
    adx_length: np.int16
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Directional Movement Index (DMI) indicators.

    Computes three components of the DMI system:
    - +DI (Positive Directional Indicator)
    - -DI (Negative Directional Indicator) 
    - ADX (Average Directional Movement Index)

    Args:
        high (np.ndarray): Array of high prices.
        low (np.ndarray): Array of low prices.
        close (np.ndarray): Array of closing prices.
        di_length (int): Period for DI calculations.
        adx_length (int): Smoothing period for ADX calculation.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Three arrays containing:
            - +DI values
            - -DI values
            - ADX values
    """

    n = high.shape[0]

    change_high = np.empty(n, dtype=np.float64)
    change_low = np.empty(n, dtype=np.float64)
    change_high[0] = np.nan
    change_low[0] = np.nan

    for i in range(1, n):
        change_high[i] = high[i] - high[i - 1]
        change_low[i] = low[i - 1] - low[i]

    tr_values = tr(high, low, close, handle_nan=False)

    plus_dm = np.empty(n, dtype=np.float64)
    plus_dm[0] = np.nan

    for i in range(1, n):
        if change_high[i] > change_low[i] and change_high[i] > 0:
            plus_dm[i] = change_high[i]
        else:
            plus_dm[i] = 0.0

    minus_dm = np.empty(n, dtype=np.float64)
    minus_dm[0] = np.nan

    for i in range(1, n):
        if change_low[i] > change_high[i] and change_low[i] > 0:
            minus_dm[i] = change_low[i]
        else:
            minus_dm[i] = 0.0

    rma_tr = rma(tr_values, di_length)
    rma_plus_dm = rma(plus_dm, di_length)
    rma_minus_dm = rma(minus_dm, di_length)

    plus = 100 * rma_plus_dm / rma_tr
    minus = 100 * rma_minus_dm / rma_tr
    dx = np.abs(plus - minus) / (plus + minus)

    for i in range(dx.shape[0]):
        if plus[i] + minus[i] == 0:
            dx[i] = np.nan

    adx = 100 * rma(dx, adx_length)
    return plus, minus, adx