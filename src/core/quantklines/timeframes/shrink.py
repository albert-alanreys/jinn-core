import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:, :](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def shrink(
    lower_tf_source: np.ndarray,
    lower_tf_time: np.ndarray,
    target_tf_time: np.ndarray
) -> np.ndarray:
    """
    Adapt lower timeframe data to current timeframe by aligning values.

    Maps values from higher resolution (lower timeframe) to main timeframe,
    creating a 2D array where each row represents a main timeframe bar
    with corresponding lower timeframe values.

    Args:
        lower_tf_source (np.ndarray): Data values from lower timeframe
        lower_tf_time (np.ndarray): Timestamps of lower (source) timeframe
        target_tf_time (np.ndarray): Timestamps of main (target) timeframe

    Returns:
        np.ndarray: 2D array with lower TF values aligned to main TF
    """

    n_lower = lower_tf_time.shape[0]
    n_target = target_tf_time.shape[0]
    
    if n_target < 2:
        return np.full((n_target, n_lower), np.nan)

    lower_duration = lower_tf_time[1] - lower_tf_time[0]
    target_duration = target_tf_time[1] - target_tf_time[0]
    subbars = int(target_duration / lower_duration + 0.5)

    result = np.full((n_target, subbars), np.nan)

    target_idx = 0
    lower_idx = 0

    k_offset = int(
        (target_tf_time[1] - lower_tf_time[0]) /
        lower_duration + 0.5
    )
    k = subbars - k_offset

    while target_idx < n_target and lower_idx < n_lower:
        time_close = target_tf_time[target_idx] + target_duration

        if lower_tf_time[lower_idx] < time_close:
            result[target_idx, k] = lower_tf_source[lower_idx]
            lower_idx += 1
            k += 1
        else:
            target_idx += 1
            k = 0

    return result