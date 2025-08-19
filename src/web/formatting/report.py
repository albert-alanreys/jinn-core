from datetime import datetime, timezone

import numpy as np

from src.shared.utils import adjust_vectorized
from .constants import (
    METRIC_SUFFIXES,
    CLOSE_SIGNAL_CODES,
    ENTRY_SIGNAL_CODES,
    TRADE_TYPE_LABELS
)


def format_overview_metrics(
    metrics: dict,
    completed_deals_log: np.ndarray
) -> dict:
    """
    Formats overview metrics by applying appropriate suffixes
    (e.g., ' USDT', '%') to each value in the 'all' fields
    of the primary metrics based on the metric title.
    Also formats the equity curve using timestamps from
    completed deals and corresponding equity values.

    Args:
        metrics (dict): Dictionary containing:
            - 'primary': List of metric dictionaries
                         with 'title' and 'all' values
            - 'equity': List or array of equity values
        completed_deals_log (np.ndarray): Array of completed deal records
                                          used to extract equity timestamps

    Returns:
        dict: Dictionary with:
            - 'primary': List of formatted metric strings with suffixes
            - 'equity': List of dicts with 'time' and 'value'
                        for plotting the equity curve
    """

    result = {'primary': [], 'equity': []}

    if completed_deals_log.size == 0:
        return result

    formatted_primary_metrics = []

    for metric in metrics['primary']:
        title = metric['title']
        values = metric['all']
        suffixes = METRIC_SUFFIXES.get(title, [''] * len(values))

        for value, suffix in zip(values, suffixes):
            formatted_primary_metrics.append(f'{value}{suffix}')

    timestamps = completed_deals_log[:, 4] * 0.001
    equity_values = adjust_vectorized(metrics['equity'], 0.01)
    formatted_equity = []
    used_timestamps = set()

    for t, v in zip(timestamps, equity_values):
        while t in used_timestamps:
            t += 1

        used_timestamps.add(t)
        formatted_equity.append({'time': t, 'value': v})

    return {
        'primary': formatted_primary_metrics,
        'equity': formatted_equity
    }


def format_performance_metrics(metrics: list) -> list:
    """
    Formats performance metrics by applying appropriate suffixes
    (e.g., ' USDT', '%') to each value in the 'all', 'long',
    and 'short' fields based on the metric title.

    Args:
        metrics (list): List of metric dictionaries, each containing 'title',
                        'all', 'long', and 'short' numeric series

    Returns:
        list: List of formatted metric dictionaries
              with suffixed string values
    """

    return _format_metrics(metrics)


def format_trade_metrics(metrics: list) -> list:
    """
    Formats trade-related metrics by applying appropriate suffixes
    (e.g., ' USDT', '%') to each value in the 'all', 'long',
    and 'short' fields based on the metric title.

    Args:
        metrics (list): List of metric dictionaries, each containing 'title',
                        'all', 'long', and 'short' numeric series

    Returns:
        list: List of formatted metric dictionaries
              with suffixed string values
    """

    return _format_metrics(metrics)


def format_risk_metrics(metrics: list) -> list:
    """
    Formats risk-related metrics by applying appropriate suffixes
    (e.g., ' USDT', '%') to each value in the 'all', 'long',
    and 'short' fields based on the metric title.

    Args:
        metrics (list): List of metric dictionaries, each containing 'title',
                        'all', 'long', and 'short' numeric series

    Returns:
        list: List of formatted metric dictionaries
              with suffixed string values
    """

    return _format_metrics(metrics)


def format_trades(
    completed_deals_log: np.ndarray,
    open_deals_log: np.ndarray
) -> list:
    """
    Formats completed and open trades into structured rows
    for tabular display, enriching each trade with signal
    labels, timestamps, and formatted numerical values.

    Args:
        completed_deals_log (np.ndarray): 2D array of closed trade data
        open_deals_log (np.ndarray): 2D array of currently open trade data

    Returns:
        list: List of formatted trade rows,
              each represented as a list of strings
    """

    completed_deals = completed_deals_log[:, :12]
    result = []
    num = 1

    for deal in completed_deals:
        code = deal[1] - (deal[1] % 100)
        n_deal = int(deal[1] % 100)
        order_signal = (
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
            order_signal,
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
        num += 1

    if np.all(np.isnan(open_deals_log)):
        return result

    open_deals = open_deals_log.reshape((-1, 5))
    mask = ~np.isnan(open_deals).any(axis=1)
    open_deals = open_deals[mask]

    for deal in open_deals:
        code = deal[1] - (deal[1] % 100)
        n_deal = int(deal[1] % 100)
        order_signal = (
            f'{ENTRY_SIGNAL_CODES[code]}' +
            (f' | #{n_deal}' if n_deal > 0 else '')
        )

        formatted = [
            str(num),
            TRADE_TYPE_LABELS[deal[0]][1],
            TRADE_TYPE_LABELS[deal[0]][0],
            order_signal,
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
        num += 1

    return result


def _format_metrics(metrics: list) -> list:
    """
    Internal function that applies suffix formatting to each metric group.
    It processes the 'all', 'long', and 'short' value lists for each
    metric title using the predefined suffixes from METRIC_SUFFIXES.

    Args:
        metrics (list):
            List of raw metric dictionaries with:
            - 'title': Name of the metric
            - 'all': List of values for all trades
            - 'long': List of values for long trades
            - 'short': List of values for short trades

    Returns:
        list: List of formatted metric dictionaries
              with suffixed string values
    """

    formatted = []

    for metric in metrics:
        title = metric['title']
        formatted_metric = {
            'title': [title],
            'all': _apply_suffix(title, metric['all']),
            'long': _apply_suffix(title, metric['long']),
            'short': _apply_suffix(title, metric['short']),
        }
        formatted.append(formatted_metric)

    return formatted


def _apply_suffix(title: str, values: list) -> list:
    """
    Internal helper that applies suffixes to a list of values
    based on the metric title. If a value is NaN, an empty
    string is returned for that position.

    Args:
        title (str): Metric title used to look up appropriate suffixes
        values (list): List of numerical values to be formatted

    Returns:
        list: List of strings, where each numeric value is formatted
              with its corresponding suffix.
    """

    suffixes = METRIC_SUFFIXES.get(title, [])
    formatted = []

    for i, value in enumerate(values):
        if np.isnan(value):
            formatted.append('')
        else:
            suffix = suffixes[i] if i < len(suffixes) else ''
            formatted.append(f'{value}{suffix}')

    return formatted