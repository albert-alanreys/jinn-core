from time import time

from numpy import ndarray


def has_first_historical_kline(klines: list | ndarray, start: int) -> bool:
    """
    Check if the first kline's timestamp is at least one full interval
    after the start time.

    Args:
        klines (list | ndarray): Klines, each with timestamp at index 0.
        start (int): Start timestamp in milliseconds.

    Returns:
        bool: True if there could be at least one kline interval between
              the start and the first kline timestamp. False otherwise.
    """

    kline_ms = klines[1][0] - klines[0][0]
    return bool((klines[0][0] - start) // kline_ms)


def has_last_historical_kline(klines: list | ndarray) -> bool:
    """
    Determines whether the most recent closed kline is present
    in the given data.

    Args:
        klines (list | ndarray): Klines, each with timestamp at index 0.

    Returns:
        bool: True if the last kline is the most recent closed one.
              False if a newer closed kline is likely available.
    """

    now_ms = int(time() * 1000)
    kline_ms = klines[1][0] - klines[0][0]
    return (now_ms - klines[-1][0]) // kline_ms < 2


def has_realtime_kline(klines: list | ndarray) -> bool:
    """
    Check if the last kline is realtime (not fully closed).

    Args:
        klines (list | ndarray): Klines, each with timestamp at index 0.

    Returns:
        bool: True if last kline is realtime (still forming), False if closed.
    """

    now_ms = int(time() * 1000)
    kline_ms = klines[1][0] - klines[0][0]
    return not (now_ms - klines[-1][0]) // kline_ms