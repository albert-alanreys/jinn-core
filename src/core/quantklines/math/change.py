import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.int16),
    cache=True, nopython=True, nogil=True
)
def change(source: np.ndarray, length: np.int16) -> np.ndarray:
    return (
        source - np.concatenate(
            (np.full(length, np.nan), source[: -length])
        )
    )