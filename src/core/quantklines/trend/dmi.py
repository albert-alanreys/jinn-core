import numpy as np
import numba as nb


@nb.jit(
    nb.types.Tuple((nb.float64[:], nb.float64[:], nb.float64[:]))(
        nb.float64[:], nb.float64[:], nb.float64[:], nb.int16, nb.int16
    ),
    cache=True, nopython=True, nogil=True
)
def dmi(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    di_length: np.int16,
    adx_length: np.int16
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # change_high
    change_high = (
        high - np.concatenate((np.full(1, np.nan), high[: -1]))
    )

    # change_low
    change_low = (
        low - np.concatenate((np.full(1, np.nan), low[: -1]))
    )

    # tr
    hl = high - low
    hc = np.absolute(
        high - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    lc = np.absolute(
        low - np.concatenate((np.full(1, np.nan), close[:-1]))
    )
    hl[0] = np.nan
    hc[0] = np.nan
    lc[0] = np.nan
    tr = np.maximum(np.maximum(hl, hc), lc)

    # rma_tr
    rma_tr = tr.copy()
    alpha = 1 / di_length
    na_sum = np.isnan(rma_tr).sum()
    rma_tr[: di_length + na_sum - 1] = np.nan
    rma_tr[di_length + na_sum - 1] = (
        tr[na_sum : di_length + na_sum].mean()
    )

    for i in range(di_length + na_sum, rma_tr.shape[0]):
        rma_tr[i] = alpha * rma_tr[i] + (1 - alpha) * rma_tr[i - 1]

    # rma_plus_dmi
    plus_dmi = change_high.copy()
    plus_dmi[~((change_high > -change_low) & (change_high > 0))] = 0
    plus_dmi[0] = np.nan

    rma_plus_dmi = plus_dmi.copy()
    alpha = 1 / di_length
    na_sum = np.isnan(rma_plus_dmi).sum()
    rma_plus_dmi[: di_length + na_sum - 1] = np.nan
    rma_plus_dmi[di_length + na_sum - 1] = (
        plus_dmi[na_sum : di_length + na_sum].mean()
    )

    for i in range(di_length + na_sum, plus_dmi.shape[0]):
        rma_plus_dmi[i] = (alpha * rma_plus_dmi[i] +
            (1 - alpha) * rma_plus_dmi[i - 1])

    # rma_minus_dmi
    minus_dmi = -change_low.copy()
    minus_dmi[~((-change_low > change_high) & (-change_low > 0))] = 0
    minus_dmi[0] = np.nan

    rma_minus_dmi = minus_dmi.copy()
    alpha = 1 / di_length
    na_sum = np.isnan(rma_minus_dmi).sum()
    rma_minus_dmi[: di_length + na_sum - 1] = np.nan
    rma_minus_dmi[di_length + na_sum - 1] = (
        minus_dmi[na_sum : di_length + na_sum].mean()
    )

    for i in range(di_length + na_sum, minus_dmi.shape[0]):
        rma_minus_dmi[i] = (alpha * rma_minus_dmi[i] +
            (1 - alpha) * rma_minus_dmi[i - 1])

    # plus
    plus = 100 * rma_plus_dmi / rma_tr

    # minus
    minus = 100 * rma_minus_dmi / rma_tr
    
    # rma
    diff = plus - minus
    sum = plus + minus
    sum[sum == 0] = 1
    source = np.absolute(diff) / sum
    rma = source.copy()
    alpha = 1 / adx_length
    na_sum = np.isnan(rma).sum()
    rma[: adx_length + na_sum - 1] = np.nan
    rma[adx_length + na_sum - 1] = (
        source[na_sum : adx_length + na_sum].mean()
    )

    for i in range(adx_length + na_sum, source.shape[0]):
        rma[i] = (alpha * rma[i] +
            (1 - alpha) * rma[i - 1])

    # adx
    adx = 100 * rma

    # values
    values = (plus, minus, adx)
    return values