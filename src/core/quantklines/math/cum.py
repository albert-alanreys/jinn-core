import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:],),
    cache=True, nopython=True, nogil=True
)
def cum(source: np.ndarray) -> np.ndarray:
    return source.cumsum()