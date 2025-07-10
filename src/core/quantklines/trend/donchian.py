import numpy as np
import numba as nb

from src.core.quantklines.utils import highest, lowest


@nb.njit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.int16
    ), 
    cache=True,
    nogil=True
)
def donchian(
    high: np.ndarray,
    low: np.ndarray,
    length: np.int16
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Donchian Channel indicators (upper, lower, middle bands).

    Args:
        high (np.ndarray): Array of high prices.
        low (np.ndarray): Array of low prices.
        length (int): Lookback period for calculations.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Three arrays containing:
            - Upper band values
            - Lower band values
            - Middle band values
    """

    upper = highest(high, length)
    lower = lowest(low, length)
    middle = (upper + lower) / 2

    return upper, lower, middle