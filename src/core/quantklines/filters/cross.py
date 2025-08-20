import numpy as np
import numba as nb


@nb.njit(nb.boolean[:](nb.float64[:], nb.float64[:]), cache=True, nogil=True)
def cross(source1: np.ndarray, source2: np.ndarray) -> np.ndarray:
    """
    Detects crossover points between two data series.

    The function identifies points where:
    - source1 crosses above source2 (from below)
    - source1 crosses below source2 (from above)

    Args:
        source1: First input data series
        source2: Second input data series

    Returns:
        np.ndarray[bool]: Boolean array with True values at crossover points
    """

    diff = source1 - source2
    prev_diff = np.concatenate((np.full(1, np.nan), diff[: -1]))
    return ((diff > 0) & (prev_diff <= 0)) | ((diff < 0) & (prev_diff >= 0))