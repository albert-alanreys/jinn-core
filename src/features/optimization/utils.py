from typing import Any

import numpy as np


def create_train_test_windows(
    market_data: dict[str, Any],
    config: Any
) -> dict[str, int]:
    """
    Create indices for train and test datasets.

    Splits the data into train/test sets using the ratio specified in config.
    Train set comes first, followed immediately by test set.

    Args:
        market_data: Dataset containing klines and metadata
        config: Configuration with window sizes as ratios (0.0-1.0)

    Returns:
        dict[str, int]:
            Dictionary with index boundaries for train and test sets
    """

    total_klines = len(market_data['klines'])
    
    train_size = int(total_klines * config.train_window_klines)
    test_size = int(total_klines * config.validation_window_klines)
    
    if train_size + test_size > total_klines:
        test_size = total_klines - train_size
    
    return {
        'train_start': 0,
        'train_end': train_size,
        'test_start': train_size,
        'test_end': train_size + test_size
    }


def create_window_data(
    market_data: dict[str, Any],
    window: dict[str, int],
    data_type: str
) -> dict[str, Any]:
    """
    Extract market data for a given window.

    Returns either training or testing subset defined by window indices.

    Args:
        market_data: Full dataset with klines and feeds
        window: Window index boundaries
        data_type: 'train' or 'test' subset

    Returns:
        dict[str, Any]: Window-specific dataset
    """

    if data_type == 'train':
        start_idx = window['train_start']
        end_idx = window['train_end']
    else:
        start_idx = window['test_start']
        end_idx = window['test_end']

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