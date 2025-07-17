import numpy as np
import numba as nb

from src.core.quantklines.math import sma, stdev


@nb.njit(
    nb.float64[:](nb.float64[:], nb.int16, nb.float32),
    cache=True,
    nogil=True
)
def bbw(
    source: np.ndarray,
    length: np.int16,
    mult: np.float32
) -> np.ndarray:
    """
    Calculate Bollinger Bands Width (BBW) indicator values.

    The function computes the normalized width between upper and
    lower Bollinger Bands, expressed as a percentage of the middle band (SMA).

    Args:
        source (np.ndarray): Input price series
        length (int): Period length for moving average and standard deviation
        mult (float): Multiplier for standard deviation bands width

    Returns:
        np.ndarray: Array containing Bollinger Bands Width values
    """

    mean = sma(source, length)
    std = stdev(source, length)

    upper = mean + mult * std
    lower = mean - mult * std

    return (upper - lower) / mean