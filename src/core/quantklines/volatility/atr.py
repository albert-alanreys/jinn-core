import numpy as np
import numba as nb

from src.core.quantklines.math import rma
from .tr import tr


@nb.njit(
    nb.float64[:](
        nb.float64[:], nb.float64[:], nb.float64[:], nb.int16
    ),
    cache=True,
    nogil=True
)
def atr(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    length: np.int16
) -> np.ndarray:
    """
    Calculate the Average True Range (ATR) indicator.

    The function computes a smoothed moving average of TR values over the
    specified period. Uses Wilder's smoothing method (RMA) for calculation.

    Args:
        high (np.ndarray): High price series.
        low (np.ndarray): Low price series.
        close (np.ndarray): Close price series.
        length (int): Period length for smoothing.

    Returns:
        np.ndarray: ATR values array.
    """

    tr_values = tr(high, low, close, True)
    return rma(tr_values, length)