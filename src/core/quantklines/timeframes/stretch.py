from __future__ import annotations

import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:,:](nb.float64[:,:], nb.float64[:], nb.float64[:]),
    cache=True,
    nogil=True
)
def stretch(
    higher_tf_data: np.ndarray,
    higher_tf_time: np.ndarray,
    target_tf_time: np.ndarray
) -> np.ndarray:
    """
    Align higher timeframe data to the main timeframe by expanding values.

    Each row of `higher_tf_data` corresponds to a higher timeframe bar.
    This function stretches them to match `target_tf_time` resolution.

    Args:
        higher_tf_data: Data values from higher timeframe
        higher_tf_time: Timestamps of higher timeframe
        target_tf_time: Timestamps of target timeframe

    Returns:
        np.ndarray: 2D Array with higher TF values expanded to main TF
    """

    n_higher, n_features = higher_tf_data.shape
    n_target = target_tf_time.shape[0]

    result = np.full((n_target, n_features), np.nan)

    if n_higher < 2:
        return result

    duration = higher_tf_time[1] - higher_tf_time[0]
    next_boundary = higher_tf_time[1]

    higher_idx = 0
    for target_idx in range(1, n_target):
        if target_tf_time[target_idx] >= next_boundary:
            result[target_idx, :] = higher_tf_data[higher_idx, :]
            higher_idx += 1

            if higher_idx < n_higher:
                next_boundary = higher_tf_time[higher_idx] + duration
            else:
                next_boundary = np.inf
        else:
            result[target_idx, :] = result[target_idx - 1, :]

    return result