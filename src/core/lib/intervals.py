import numpy as np
import numba as nb


@nb.jit(
    nb.float64[:](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True, nopython=True, nogil=True
)
def stretch(
    source: np.ndarray,
    main_time: np.ndarray,
    higher_time: np.ndarray
) -> np.ndarray:
    values = np.full(main_time.shape[0], np.nan)

    if source.shape[0] < 2:
        return values

    duration = higher_time[1] - higher_time[0]
    time_close = higher_time[0] + duration

    i = 0
    for j in range(1, main_time.shape[0]):
        if time_close == main_time[j]:
            values[j] = source[i]
            i += 1

            if i < source.shape[0]:
                time_close = higher_time[i] + duration
        else:
            values[j] = values[j - 1]
    
    return values


@nb.jit(
    nb.float64[:, :](nb.float64[:], nb.float64[:], nb.float64[:]),
    cache=True, nopython=True, nogil=True
)
def shrink(
    source: np.ndarray,
    main_time: np.ndarray,
    lower_time: np.ndarray
) -> np.ndarray:
    if main_time.shape[0] < 2:
        return np.full((main_time.shape[0], lower_time.shape[0]), np.nan)

    main_duration = main_time[1] - main_time[0]
    sub_duration = lower_time[1] - lower_time[0]
    subbars = round(main_duration / sub_duration)
    values = np.full((main_time.shape[0], subbars), np.nan)

    i = 0
    j = 0
    k = round(subbars - (main_time[1] - lower_time[0]) / sub_duration)
    while i < main_time.shape[0] and j < lower_time.shape[0]:
        time_close = main_time[i] + main_duration

        if lower_time[j] < time_close:
            values[i, k] = source[j]
            j += 1
            k += 1
        else:
            i += 1
            k = 0

    return values