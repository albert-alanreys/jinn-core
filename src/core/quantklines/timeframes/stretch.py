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