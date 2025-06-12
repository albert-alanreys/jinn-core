import numpy as np
import numba as nb


@nb.jit( 
    nb.types.Tuple((nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.float64[:], nb.float32, nb.int16
    ),
    cache=True, nopython=True, nogil=True
)
def supertrend(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    factor: np.float32,
    atr_length: np.int16
) -> tuple[np.ndarray, np.ndarray]:
    # tr
    hl = high - low
    hc = np.absolute(
        high - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    lc = np.absolute(
        low - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    hc[0] = abs(high[0] - close[0])
    lc[0] = abs(low[0] - close[0])
    tr = np.maximum(np.maximum(hl, hc), lc)

    # atr
    atr = tr.copy()
    alpha = 1 / atr_length
    na_sum = np.isnan(atr).sum()
    atr[: atr_length + na_sum - 1] = np.nan
    atr[atr_length + na_sum - 1] = tr[na_sum : atr_length + na_sum].mean()

    for i in range(atr_length + na_sum, atr.shape[0]):
        atr[i] = alpha * atr[i] + (1 - alpha) * atr[i - 1]

    # values
    hl2 = (high + low) / 2
    upper_band = hl2 + factor * atr
    lower_band = hl2 - factor * atr
    indicator = np.full(atr.shape[0], np.nan)
    direction = np.full(atr.shape[0], np.nan)

    for i in range(1, atr.shape[0]):
        prev_indicator = indicator[i - 1]

        if not np.isnan(upper_band[i - 1]):
            prev_upper_band = upper_band[i - 1]
        else:
            prev_upper_band = 0

        if not np.isnan(lower_band[i - 1]):
            prev_lower_band = lower_band[i - 1]
        else:
            prev_lower_band = 0

        if not (upper_band[i] < prev_upper_band
                or close[i - 1] > prev_upper_band):
            upper_band[i] = prev_upper_band

        if not (lower_band[i] > prev_lower_band
                or close[i - 1] < prev_lower_band):
            lower_band[i] = prev_lower_band

        if np.isnan(atr[i - 1]):
            direction[i] = 1
        elif prev_indicator == prev_upper_band:
            if close[i] > upper_band[i]:
                direction[i] = -1
            else:
                direction[i] = 1
        else:
            if close[i] < lower_band[i]:
                direction[i] = 1
            else:
                direction[i] = -1

        if direction[i] == -1:
            indicator[i] = lower_band[i]
        else:
            indicator[i] = upper_band[i]

    values = (indicator, direction)
    return values