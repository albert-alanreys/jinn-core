import numba as nb
import numpy as np


@nb.jit(
    nb.float64(nb.float64, nb.float64),
    cache=True, nopython=True, nogil=True
)
def adjust(value: float, step: float) -> float:
    """
    Rounds a value to the nearest multiple of step with 10 decimal precision.

    Args:
        value (float): Input value.
        step (float): Adjustment step size.

    Returns:
        float: Adjusted and rounded value.
    """

    return round(round(value / step) * step, 10)


@nb.guvectorize(
    ['void(float64[:], float64, float64[:])'], '(n),()->(n)',
    nopython=True, cache=True
)
def adjust_vectorized(
    values: np.ndarray,
    step: float,
    result: np.ndarray
) -> np.ndarray:
    """
    Vectorized adjustment of an array of float values to the nearest multiple
    of a given step with 10 decimal precision.

    For each element in the input array:
    - If the value is NaN, the result will also be NaN.
    - Otherwise, the value is rounded to the nearest multiple of `step`,
      and the result is rounded to 10 decimal places.

    Args:
        values (float64[:]): 1D array of input float values.
        step (float64): Adjustment step size.
        result (float64[:]): 1D array where the adjusted values will be stored.

    Returns:
        None: The results are written in-place to the `result` array.
    """

    for i in range(values.shape[0]):
        val = values[i]

        if np.isnan(val):
            result[i] = np.nan
        else:
            result[i] = round(round(val / step) * step, 10)