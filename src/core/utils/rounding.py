import numba as nb


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