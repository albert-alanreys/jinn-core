def adjust(value: float, step: float, digits: int = 8) -> float:
    """
    Adjust a value to the specified step and round to a fixed number of digits.

    Args:
        value (float): The original value to adjust.
        step (float): Step size (e.g., price or quantity precision).
        digits (int): Number of decimal places to round to. Defaults to 8.

    Returns:
        float: Adjusted and rounded value.
    """
    return round(round(value / step) * step, digits)