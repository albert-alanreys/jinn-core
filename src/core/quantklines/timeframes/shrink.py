import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:, :, :](nb.float64[:, :], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def shrink(
    lower_tf_data: np.ndarray,
    lower_tf_time: np.ndarray,
    target_tf_time: np.ndarray
) -> np.ndarray:
    """
    Align lower timeframe data to the main timeframe by grouping values.

    Each row of `lower_tf_data` corresponds to a lower timeframe bar.
    This function groups them into blocks according to target timeframe.

    Args:
        lower_tf_data: Data values from lower timeframe
        lower_tf_time: Timestamps of lower timeframe
        target_tf_time: Timestamps of target timeframe

    Returns:
        np.ndarray: 3D array with lower TF values aligned to main TF
    """

    n_lower, n_features = lower_tf_data.shape
    n_target = target_tf_time.shape[0]
    
    if n_target < 2 or n_lower < 1:
        return np.full((n_target, 0, n_features), np.nan)

    lower_duration = lower_tf_time[1] - lower_tf_time[0]
    target_duration = target_tf_time[1] - target_tf_time[0]
    subbars = int(target_duration / lower_duration + 0.5)

    result = np.full((n_target, n_features, subbars), np.nan)

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
            result[target_idx, :, k] = lower_tf_data[lower_idx, :]
            lower_idx += 1
            k += 1
        else:
            target_idx += 1
            k = 0

    return result