import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:, :](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def shrink(
    source: np.ndarray,
    main_time: np.ndarray,
    lower_time: np.ndarray
) -> np.ndarray:
    """
    Adapt lower timeframe data to current timeframe by aligning values.

    Maps values from higher resolution (lower timeframe) to main timeframe,
    creating a 2D array where each row represents a main timeframe bar
    with corresponding lower timeframe values.

    Args:
        source (np.ndarray): Data values from lower timeframe.
        main_time (np.ndarray): Timestamps of main (target) timeframe.
        lower_time (np.ndarray): Timestamps of lower (source) timeframe.

    Returns:
        np.ndarray: 2D array with lower TF values aligned to main TF.
    """

    n = main_time.shape[0]
    m = lower_time.shape[0]
    
    if n < 2:
        return np.full((n, m), np.nan)

    main_duration = main_time[1] - main_time[0]
    sub_duration = lower_time[1] - lower_time[0]
    subbars = int(main_duration / sub_duration + 0.5)

    result = np.full((n, subbars), np.nan)

    i = 0
    j = 0

    k_offset = int((main_time[1] - lower_time[0]) / sub_duration + 0.5)
    k = subbars - k_offset

    while i < n and j < m:
        time_close = main_time[i] + main_duration

        if lower_time[j] < time_close:
            result[i, k] = source[j]
            j += 1
            k += 1
        else:
            i += 1
            k = 0

    return result