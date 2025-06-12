import numpy as np
import numba as nb


def daily_vwap_with_reset(
    time: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> np.ndarray:
    typical_price = (high + low + close) / 3
    vwap = np.full_like(close, np.nan)
    cum_tpv = 0.0
    cum_vol = 0.0
    current_day = -1

    for i in range(len(time)):
        # день в формате UTC
        utc_day = int((time[i] / 1000) // 86400)

        if utc_day != current_day:
            # новый день — сбрасываем накопления
            current_day = utc_day
            cum_tpv = 0.0
            cum_vol = 0.0
            cum_tpv += typical_price[i] * volume[i]
            cum_vol += volume[i]
            vwap[i] = cum_tpv / cum_vol if cum_vol > 0 else np.nan

    return vwap


def vwap(
    time: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray
) -> np.ndarray:
    typical_price = (high + low + close) / 3
    vwap = np.full_like(close, np.nan)
    cum_tpv = 0.0
    cum_vol = 0.0
    current_day = -1

    for i in range(len(time)):
        # день в формате UTC
        utc_day = int((time[i] / 1000) // 86400)

        if utc_day != current_day:
            # новый день — сбрасываем накопления
            current_day = utc_day
            cum_tpv = 0.0
            cum_vol = 0.0
            cum_tpv += typical_price[i] * volume[i]
            cum_vol += volume[i]
            vwap[i] = cum_tpv / cum_vol if cum_vol > 0 else np.nan

    return vwap