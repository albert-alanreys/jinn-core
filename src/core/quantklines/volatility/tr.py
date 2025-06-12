import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:], nb.boolean),
    cache=True, nopython=True, nogil=True
)
def tr(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    handle_na: np.bool_
) -> np.ndarray:
    hl = high - low
    hc = np.absolute(
        high - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    lc = np.absolute(
        low - np.concatenate((np.full(1, np.nan), close[:-1]))
    )

    if handle_na:
        hc[0] = abs(high[0] - close[0])
        lc[0] = abs(low[0] - close[0])
    else:
        hl[0] = np.nan
        hc[0] = np.nan
        lc[0] = np.nan

    values = np.maximum(np.maximum(hl, hc), lc)
    return values
