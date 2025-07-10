import numpy as np
import numba as nb

from src.core.quantklines.math import rma


@nb.njit(nb.float64[:](nb.float64[:], nb.int16), cache=True, nogil=True)
def rsi(source: np.ndarray, length: np.int16) -> np.ndarray:
    """
    Calculate RSI (Relative Strength Index).

    Args:
        source (np.ndarray): Input series (leading NaNs are skipped).
        length (int): RSI period length.

    Returns:
        np.ndarray: RSI values array.
    """

    u = source - np.concatenate((np.full(1, np.nan), source[: -1]))
    d = np.concatenate((np.full(1, np.nan), source[: -1])) - source
    u[u < 0] = 0
    d[d < 0] = 0

    rma_u = rma(u, length)
    rma_d = rma(d, length)
    return 100 - 100 / (1 + rma_u / rma_d)