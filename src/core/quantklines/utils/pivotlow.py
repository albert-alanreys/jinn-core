import numpy as np
import numba as nb


@nb.njit(
    nb.float64[:](nb.float64[:], nb.int16, nb.int16),
    cache=True,
    nogil=True
)
def pivotlow(
    source: np.ndarray,
    leftbars: np.int16,
    rightbars: np.int16
) -> np.ndarray:
    """
    Identify pivot lows in a series over specified left and
    right lookback windows.

    The function scans the input series to find local minima (pivot lows)
    where the center value is lower than all values within the left and right
    windows. The pivot low is marked at the right edge of the right window.

    Args:
        source (np.ndarray): Input price series
                             (leading and trailing NaNs are skipped)
        leftbars (int): Number of bars to look back (left window size)
        rightbars (int): Number of bars to look forward (right window size)

    Returns:
        np.ndarray: Array with pivot low values marked
                    at their right window edges,
                    NaN elsewhere
    """

    n = source.shape[0]
    result = np.full(n, np.nan, dtype=np.float64)

    for i in range(leftbars, n - rightbars):
        center_idx = i
        pivot_idx = i + rightbars
        center = source[center_idx]

        if np.isnan(center):
            continue

        is_pivot = True

        for j in range(i - leftbars, i):
            if not np.isnan(source[j]) and source[j] <= center:
                is_pivot = False
                break

        if not is_pivot:
            continue

        for j in range(i + 1, i + rightbars + 1):
            if not np.isnan(source[j]) and source[j] < center:
                is_pivot = False
                break

        if is_pivot:
            result[pivot_idx] = center

    return result