from __future__ import annotations

import numpy as np
import numba as nb


@nb.njit(nb.float64[:](nb.float64[:],), cache=True, nogil=True)
def cum(source: np.ndarray) -> np.ndarray:
    """
    Calculate the cumulative sum of elements in the input array.

    Args:
        source: Input data series

    Returns:
        np.ndarray: Array containing the cumulative sum of the input elements
    """

    return source.cumsum()