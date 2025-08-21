from typing import Any

import numpy as np


def create_walkforward_windows(
    market_data: dict[str, Any],
    config: Any
) -> list[dict[str, int]]:
    """
    Create Walk-Forward Analysis windows.

    Builds sequential train/validation windows from candle data
    using sliding window approach.

    Args:
        market_data: Dataset containing klines and metadata
        config: OptimizationConfig with window sizes and step

    Returns:
        list[dict[str, int]]: List of window index boundaries
    """

    windows = []
    total_klines = len(market_data['klines'])
    start_idx = 0

    while True:
        train_end_idx = start_idx + config.train_window_klines
        val_end_idx = train_end_idx + config.validation_window_klines

        if val_end_idx > total_klines:
            break

        windows.append({
            'train_start': start_idx,
            'train_end': train_end_idx,
            'validation_start': train_end_idx,
            'validation_end': val_end_idx
        })
        start_idx += config.step_klines

    return windows


def latin_hypercube_sampling(
    param_space: dict[str, list[Any]],
    n_samples: int
) -> list[dict[str, Any]]:
    """
    Generate parameter samples using Latin Hypercube Sampling.

    Ensures uniform coverage of parameter ranges by stratified sampling.

    Args:
        param_space: Parameter space with value lists
        n_samples: Number of individuals to generate

    Returns:
        list[dict[str, Any]]: List of parameter dictionaries
    """

    samples = []
    param_keys = list(param_space.keys())
    n_params = len(param_keys)

    if n_samples <= 0 or n_params == 0:
        return samples

    lhs_matrix = np.zeros((n_samples, n_params))
    for i in range(n_params):
        lhs_matrix[:, i] = np.random.permutation(n_samples)

    for i in range(n_samples):
        individual = {}
        for j, param in enumerate(param_keys):
            values = param_space[param]
            normalized_value = lhs_matrix[i, j] / n_samples
            param_index = int(normalized_value * len(values))
            param_index = min(param_index, len(values) - 1)
            individual[param] = values[param_index]
        
        samples.append(individual)

    return samples


def create_window_data(
    market_data: dict[str, Any],
    window: dict[str, int],
    data_type: str
) -> dict[str, Any]:
    """
    Extract market data for a given window.

    Returns either training or validation subset defined by window indices.

    Args:
        market_data: Full dataset with klines and feeds
        window: Window index boundaries
        data_type: 'train' or 'validation' subset

    Returns:
        dict[str, Any]: Window-specific dataset
    """

    if data_type == 'train':
        start_idx = window['train_start']
        end_idx = window['train_end']
    else:
        start_idx = window['validation_start']
        end_idx = window['validation_end']

    slice_range = slice(start_idx, end_idx)

    window_data = {
        **market_data,
        'klines': market_data['klines'][slice_range],
        'feeds': {'klines': {}}
    }

    if market_data.get('feeds'):
        for feed_name, feed_data in market_data['feeds']['klines'].items():
            window_data['feeds']['klines'][feed_name] = feed_data[slice_range]

    return window_data