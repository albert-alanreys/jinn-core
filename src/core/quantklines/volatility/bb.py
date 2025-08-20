import numpy as np
import numba as nb

from src.core.quantklines.math import sma, stdev


@nb.njit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.int16, nb.float32
    ),
    cache=True,
    nogil=True
)
def bb(
    source: np.ndarray,
    length: np.int16,
    mult: np.float32
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Bollinger Bands indicator values.

    The function computes three lines:
    middle band (SMA), upper band (SMA + mult * std),
    and lower band (SMA - mult * std) for the given period.

    Args:
        source: Input price series
        length: Period length for moving average and standard deviation
        mult: Multiplier for standard deviation bands width

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Three arrays containing:
            - Middle band (SMA)
            - Upper band
            - Lower band
    """

    mean = sma(source, length)
    std = stdev(source, length)

    upper = mean + mult * std
    lower = mean - mult * std

    return mean, upper, lower