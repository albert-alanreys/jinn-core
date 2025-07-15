import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def stretch(
    source: np.ndarray,
    main_time: np.ndarray,
    higher_time: np.ndarray
) -> np.ndarray:
    """
    Adapt higher timeframe data to current timeframe by expanding values.

    Maps values from lower resolution (higher timeframe) to main timeframe,
    creating an array where each higher timeframe value is repeated until
    the next higher timeframe boundary.

    Args:
        source (np.ndarray): Data values from higher timeframe.
        main_time (np.ndarray): Timestamps of main (target) timeframe.
        higher_time (np.ndarray): Timestamps of higher (source) timeframe.

    Returns:
        np.ndarray: Array with higher TF values expanded to main TF.
    """

    n = main_time.shape[0]
    m = source.shape[0]

    result = np.full(n, np.nan)

    if m < 2:
        return result

    duration = higher_time[1] - higher_time[0]
    time_close = higher_time[0] + duration

    i = 0
    for j in range(1, n):
        if main_time[j] >= time_close:
            result[j] = source[i]
            i += 1

            if i < m:
                time_close = higher_time[i] + duration
        else:
            result[j] = result[j - 1]

    return result