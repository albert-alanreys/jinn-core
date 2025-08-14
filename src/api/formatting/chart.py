import numpy as np

from src.constants.deal_styles import OPEN_DEAL_STYLES, CLOSE_DEAL_STYLES
from src.constants.signal_codes import ENTRY_SIGNAL_CODES, CLOSE_SIGNAL_CODES
from src.utils.colors import decode_rgb, decode_rgb_vectorized
from src.utils.rounding import adjust_vectorized


def format_klines(klines: np.ndarray) -> list:
    """
    Formats raw klines into a list of dictionaries
    with OHLC data and timestamp.

    Args:
        klines (np.ndarray): 2D array of klines
                              [timestamp, open, high, low, close]

    Returns:
        list: Formatted klines
    """

    return [
        {
            'time': kline[0] * 0.001,
            'open': kline[1],
            'high': kline[2],
            'low': kline[3],
            'close': kline[4],
        } for kline in klines
    ]


def format_indicators(market_data: dict, indicators: dict) -> dict:
    """
    Formats indicator values and assigns corresponding colors.

    Args:
        market_data (dict): Market data containing klines
                            and price precision
        indicators (dict): Dictionary of indicators with values
                            and optional colors

    Returns:
        dict: Formatted indicator series
    """

    result = {}
    klines = market_data['klines']
    timestamps = klines[:, 0] * 0.001

    for name, indicator in indicators.items():
        values = adjust_vectorized(
            indicator['values'], market_data['p_precision']
        )
        colors = np.full(values.shape, 'transparent', dtype=object)
        color_data = indicator.get('colors') 

        if color_data is None:
            r, g, b = decode_rgb(indicator['options']['color'])
            valid_mask = ~np.isnan(values)
            colors[valid_mask] = f'rgb({r}, {g}, {b})'
        else:
            valid_mask = ~np.isnan(values)

            if np.any(valid_mask):
                rgb = decode_rgb_vectorized(
                    color_data[valid_mask].astype(np.uint32).reshape(-1, 1),
                    np.empty(
                        (np.count_nonzero(valid_mask), 3),
                        dtype=np.uint8
                    )
                )
                parts = [
                    'rgb(',
                    rgb[:, 0].astype(str),
                    ', ',
                    rgb[:, 1].astype(str),
                    ', ',
                    rgb[:, 2].astype(str),
                    ')'
                ]
                colors[valid_mask] = np.char.add(parts[0], 
                    np.char.add(parts[1], 
                    np.char.add(parts[2], 
                    np.char.add(parts[3], 
                    np.char.add(parts[4], 
                    np.char.add(parts[5], parts[6]))))))

        is_first_nan = np.isnan(values) & ~np.isnan(np.roll(values, 1))
        values[is_first_nan] = np.roll(values, 1)[is_first_nan]

        is_nan = np.isnan(values)
        values[is_nan] = klines[:, 4][is_nan]

        result[name] = [
            {'time': t, 'value': v, 'color': c}
            for t, v, c in zip(timestamps, values, colors)
        ]

    return result


def format_deals(
    completed_deals_log: np.ndarray,
    open_deals_log: np.ndarray
) -> list:
    """
    Formats completed and open deals into a list of dictionaries.

    Args:
        completed_deals_log (np.ndarray): Log of completed deals
        open_deals_log (np.ndarray): Log of currently open deals

    Returns:
        list: Formatted deals
    """

    if not completed_deals_log.size and not open_deals_log.size:
        return []

    completed_deals = completed_deals_log.tolist()
    open_deals = list(
        filter(
            lambda deal: not np.isnan(deal[0]),
            open_deals_log.reshape((-1, 5)).tolist()
        )
    )
    result = []

    def create_marker(
        position_type: int,
        signal_code: int,
        n_deal: int,
        time: float,
        size: float,
        styles_map: dict,
        is_entry: bool
    ) -> dict:
        """Helper to format a deal marker"""

        signal_codes = ENTRY_SIGNAL_CODES if is_entry else CLOSE_SIGNAL_CODES
        base_code = signal_code - (signal_code % 100)
        comment = (
            signal_codes[base_code]
            + (f' | #{n_deal}' if n_deal > 0 else '')
        )
        sign = '+' if position_type == 0 else '-'
        styles = styles_map['buy'] if position_type == 0 else styles_map['sell']

        return {
            'time': time * 0.001,
            'text': f'{comment} | {sign}{size}',
            **styles
        }

    # Add entry markers for completed deals
    for deal in completed_deals:
        result.append(create_marker(
            position_type=deal[0],
            signal_code=deal[1],
            n_deal=int(deal[1] % 100),
            time=deal[3],
            size=deal[7],
            styles_map=OPEN_DEAL_STYLES,
            is_entry=True
        ))

    # Add exit markers for completed deals
    for deal in completed_deals:
        result.append(create_marker(
            position_type=deal[0],
            signal_code=deal[2],
            n_deal=int(deal[2] % 100),
            time=deal[4],
            size=deal[7],
            styles_map=CLOSE_DEAL_STYLES,
            is_entry=False
        ))

    # Add entry markers for open deals
    for deal in open_deals:
        result.append(create_marker(
            position_type=deal[0],
            signal_code=deal[1],
            n_deal=int(deal[1] % 100),
            time=deal[2],
            size=deal[4],
            styles_map=OPEN_DEAL_STYLES,
            is_entry=True
        ))

    return sorted(result, key=lambda x: x['time'])