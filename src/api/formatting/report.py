from datetime import datetime, timezone

import numpy as np

from src.constants.metrics import OVERVIEW_METRICS, METRIC_SUFFIXES
from src.constants.signal_codes import ENTRY_SIGNAL_CODES, CLOSE_SIGNAL_CODES
from src.constants.trade_labels import TRADE_TYPE_LABELS
from src.utils.rounding import adjust_vectorized


def format_overview_metrics(
    metrics: list,
    completed_deals_log: np.ndarray
) -> dict:
    """
    Formats raw metric values into labeled structures with suffixes.

    Args:
        metrics (list): List of metric dicts with 'title'
                        and numeric series

    Returns:
        list: List of formatted metric objects
    """

    if not completed_deals_log.size:
        return []

    metrics_dict = {m['title']: m['all'] for m in metrics}
    formatted_metrics = []

    for title in OVERVIEW_METRICS:
        target_metric = metrics_dict.get(title, [])
        suffixes = METRIC_SUFFIXES.get(title, [])

        for i, value in enumerate(target_metric):
            suffix = suffixes[i] if i < len(suffixes) else ''
            formatted_metrics.append(f'{value}{suffix}')

    return formatted_metrics

@staticmethod
def format_overview_equity(
    completed_deals_log: np.ndarray,
    equity: np.ndarray
) -> list:
    """
    Formats equity curve from completed deals and equity values.

    Args:
        completed_deals_log (np.ndarray): Completed deals log
        equity (np.ndarray): Corresponding equity values

    Returns:
        list: Formatted list of equity time series points
    """

    if not completed_deals_log.size:
        return []

    timestamps = completed_deals_log[:, 4] * 0.001
    values = adjust_vectorized(equity, 0.01)

    formatted_equity = []
    used_timestamps = set()

    for t, v in zip(timestamps, values):
        adjusted_time = t

        while adjusted_time in used_timestamps:
            adjusted_time += 1

        used_timestamps.add(adjusted_time)
        formatted_equity.append({'time': adjusted_time, 'value': v})

    return formatted_equity

@staticmethod
def format_metrics(metrics: list) -> list:
    """
    Formats raw metric values into labeled structures with suffixes.

    Args:
        metrics (list): List of metric dicts with 'title'
                        and numeric series

    Returns:
        list: List of formatted metric objects
    """

    result = []

    for metric in metrics:
        title = metric['title']
        suffixes = METRIC_SUFFIXES.get(title, [])

        def apply_suffix(values):
            formatted_values = []

            for i, value in enumerate(values):
                if np.isnan(value):
                    formatted_values.append('')
                else:
                    suffix = suffixes[i] if i < len(suffixes) else ''
                    formatted_values.append(f'{value}{suffix}')

            return formatted_values

        formatted = {
            'title': [title],
            'all': apply_suffix(metric['all']),
            'long': apply_suffix(metric['long']),
            'short': apply_suffix(metric['short'])
        }
        result.append(formatted)

    return result

@staticmethod
def format_trades(
    completed_deals_log: np.ndarray,
    open_deals_log: np.ndarray
) -> list:
    """
    Formats completed and open deals into structured trade rows
    for tabular display.

    Args:
        completed_deals_log (np.ndarray): Log of closed trades
        open_deals_log (np.ndarray): Log of currently open trades

    Returns:
        list: Table of formatted trade rows
    """

    completed_deals = completed_deals_log[:, :12]
    result = []

    for num, deal in enumerate(completed_deals, 1):
        code = deal[1] - (deal[1] % 100)
        n_deal = int(deal[1] % 100)
        entry_signal = (
            f'{ENTRY_SIGNAL_CODES[code]}' +
            (f' | #{n_deal}' if n_deal > 0 else '')
        )

        code = deal[2] - (deal[2] % 100)
        n_deal = int(deal[2] % 100)
        exit_signal = (
            f'{CLOSE_SIGNAL_CODES[code]}' +
            (f' | #{n_deal}' if n_deal > 0 else '')
        )

        formatted = [
            str(num),
            TRADE_TYPE_LABELS[deal[0]][1],
            TRADE_TYPE_LABELS[deal[0]][0],
            entry_signal,
            exit_signal,
            datetime.fromtimestamp(
                timestamp=deal[3] * 0.001,
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M'),
            datetime.fromtimestamp(
                timestamp=deal[4] * 0.001,
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M'),
            f'{deal[5]} USDT',
            f'{deal[6]} USDT',
            str(deal[7]),
            f'{deal[8]} USDT',
            f'{deal[9]}%',
            f'{deal[10]} USDT',
            f'{deal[11]}%'
        ]
        result.append(formatted)

    if np.all(np.isnan(open_deals_log)):
        return result

    open_deals = open_deals_log.reshape((-1, 5))
    mask = ~np.isnan(open_deals).any(axis=1)
    open_deals = open_deals[mask]

    for num, deal in enumerate(open_deals, num + 1):
        code = deal[1] - (deal[1] % 100)
        n_deal = int(deal[1] % 100)
        entry_signal = (
            f'{ENTRY_SIGNAL_CODES[code]}' +
            (f' | #{n_deal}' if n_deal > 0 else '')
        )

        formatted = [
            str(num),
            TRADE_TYPE_LABELS[deal[0]][1],
            TRADE_TYPE_LABELS[deal[0]][0],
            entry_signal,
            '',
            datetime.fromtimestamp(
                timestamp=deal[2] * 0.001,
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M'),
            '',
            f'{deal[3]} USDT',
            '',
            str(deal[4]),
            '',
            '',
            '',
            ''
        ]
        result.append(formatted)

    return result