import numpy as np
import numba as nb


@nb.njit(nb.boolean[:](nb.float64[:], nb.float64[:]), cache=True, nogil=True)
def crossover(source1: np.ndarray, source2: np.ndarray) -> np.ndarray:
    """
    Detects upward crossover points where `source1` crosses above `source2`.

    The function returns `True` at positions where:  
    - `source1` was below or equal to `source2` on the previous step.  
    - `source1` becomes strictly above `source2` on the current step.  

    Args:
        source1 (np.ndarray): First input data series.  
        source2 (np.ndarray): Second input data series.  

    Returns:  
        np.ndarray[bool]: Boolean array with `True`
                          at upward crossover points.
    """

    diff = source1 - source2
    prev_diff = np.concatenate((np.full(1, np.nan), diff[: -1]))
    return (diff > 0) & (prev_diff <= 0)