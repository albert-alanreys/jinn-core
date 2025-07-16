import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def stretch(
    higher_tf_source: np.ndarray,
    higher_tf_time: np.ndarray,
    target_tf_time: np.ndarray
) -> np.ndarray:
    """
    Adapt higher timeframe data to current timeframe by expanding values.

    Maps values from lower resolution (higher timeframe) to main timeframe,
    creating an array where each higher timeframe value is repeated until
    the next higher timeframe boundary.

    Args:
        higher_tf_source: Data values from higher timeframe.
        higher_tf_time: Timestamps of higher (source) timeframe.
        target_tf_time: Timestamps of target (main) timeframe.

    Returns:
        np.ndarray: Array with higher TF values expanded to main TF.
    """

    n_higher = higher_tf_time.shape[0]
    n_target = target_tf_time.shape[0]

    result = np.full(n_target, np.nan)

    if n_higher < 2:
        return result

    duration = higher_tf_time[1] - higher_tf_time[0]
    next_boundary = higher_tf_time[1]

    higher_idx = 0
    for target_idx in range(1, n_target):
        if target_tf_time[target_idx] >= next_boundary:
            result[target_idx] = higher_tf_source[higher_idx]
            higher_idx += 1

            if higher_idx < n_higher:
                next_boundary = higher_tf_time[higher_idx] + duration
            else:
                next_boundary = np.inf
        else:
            result[target_idx] = result[target_idx - 1]

    return result