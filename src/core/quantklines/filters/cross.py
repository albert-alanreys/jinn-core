import numpy as np
import numba as nb


@nb.jit(
    nb.boolean[:](nb.float64[:], nb.float64[:]), 
    cache=True, nopython=True, nogil=True
)
def cross(source1: np.ndarray, source2: np.ndarray) -> np.ndarray:
    data1 = source1 - source2
    data2 = np.concatenate((np.full(1, np.nan), data1[: -1]))
    values = ((data1 > 0) & (data2 <= 0)) | ((data1 < 0) & (data2 >= 0))
    return values