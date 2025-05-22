from time import time

from numpy import ndarray


def has_first_historical_kline(klines: list | ndarray, start: int) -> bool:
    """
    Check if the first kline in the list is historical relative to
    a given start timestamp.

    Args:
        klines (list): List of klines, each with timestamp at index 0.
        start (int): Start timestamp in milliseconds.

    Returns:
        bool: True if there could be at least one kline interval between
        the start and the first kline timestamp. False otherwise.
    """
    kline_ms = int(klines[1][0]) - int(klines[0][0])
    return bool((int(klines[0][0]) - start) // kline_ms)


def has_realtime_kline(klines: list | ndarray) -> bool:
    """
    Check if the last kline is realtime (not fully closed).

    Args:
        klines (list): List of klines, each with timestamp at index 0.

    Returns:
        bool: True if last kline is realtime (still forming), False if closed.
    """
    now_ms = int(time() * 1000)
    kline_ms = int(klines[1][0]) - int(klines[0][0])
    return not bool((now_ms - int(klines[-1][0])) // kline_ms)