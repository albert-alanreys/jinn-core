from datetime import datetime, timezone
from decimal import Decimal

import numpy as np

from src.core.utils.colors import decode_rgb, decode_rgb_vectorized
from src.core.utils.rounding import adjust_vectorized
from . import constants as consts


class Formatter:
    @staticmethod
    def format_contexts(strategy_contexts: dict) -> dict:
        result = {}

        for cid, context in strategy_contexts.items():
            market_data = context['market_data']
            instance = context['instance']
            min_move = market_data['p_precision']
            precision = (
                len(str(min_move).split('.')[1])
                if '.' in str(min_move) else 0
            )

            result[cid] = {
                'name': '-'.join(
                    word.capitalize()
                    for word in context['name'].split('_')
                ),
                'exchange': context['client'].EXCHANGE,
                'symbol': market_data['symbol'],
                'market': market_data['market'].value,
                'interval': market_data['interval'],
                'minMove': min_move,
                'precision': precision,
                'strategyParams': {
                    k: v 
                    for k, v in instance.params.items() 
                    if k != 'feeds'
                },
                'indicatorOptions': instance.indicator_options
            }

        return result

    # deprecated
    @staticmethod
    def format_summary(strategy_contexts: dict) -> dict:
        result = {}

        for cid, context in strategy_contexts.items():
            result[cid] = {
                'name': '-'.join(
                    word.capitalize()
                    for word in context['name'].split('_')
                ),
                'exchange': context['client'].EXCHANGE,
                'symbol': context['market_data']['symbol'],
                'market': context['market_data']['market'].value,
                'interval': context['market_data']['interval'],
                'mintick': context['market_data']['p_precision'],
                'params': {
                    k: v for k, v in context['instance'].params.items()
                    if k != 'feeds'
                }
            }

        return result

    # deprecated
    @staticmethod
    def format_chart_details(strategy_context: dict) -> dict:
        return {
            'name': '-'.join(
                word.capitalize()
                for word in strategy_context['name'].split('_')
            ),
            'exchange': strategy_context['client'].EXCHANGE,
            'symbol': strategy_context['market_data']['symbol'],
            'market': strategy_context['market_data']['market'].value,
            'interval': strategy_context['market_data']['interval'],
            'mintick': strategy_context['market_data']['p_precision'],
            'klines': Formatter._format_klines(
                strategy_context['market_data']['klines']
            ),
            'indicators': Formatter._format_indicators(
                strategy_context['market_data'],
                strategy_context['instance'].indicators
            ),
            'indicator_options': strategy_context['instance'].indicator_options,
            'markers': Formatter._format_markers(
                strategy_context['instance'].completed_deals_log,
                strategy_context['instance'].open_deals_log
            )
        }

    @staticmethod
    def _format_klines(klines: np.ndarray) -> list:
        return [
            {
                'time': kline[0] * 0.001,
                'open': kline[1],
                'high': kline[2],
                'low': kline[3],
                'close': kline[4],
            } for kline in klines
        ]

    @staticmethod
    def _format_indicators(market_data: dict, indicators: dict) -> dict:
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

    @staticmethod
    def _format_markers(
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray
    ) -> list:
        if not completed_deals_log.size and not open_deals_log.size:
            return []

        completed_deals = completed_deals_log.reshape((-1, 13)).tolist()
        open_deals = list(
            filter(
                lambda deal: not np.isnan(deal[0]),
                open_deals_log.reshape((-1, 5)).tolist()
            )
        )

        position_size = Decimal('0.0')
        deals_count = 0

        result = []

        if len(completed_deals) == 0:
            if len(open_deals) == 0:
                return []
            
            for deal in open_deals:
                code = deal[1] - (deal[1] % 100)
                n_deal = int(deal[1] % 100)
                comment = (
                    f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                    (f' | #{n_deal}' if n_deal > 0 else '')
                )

                if deal[0] == 0:
                    styles = consts.MARKER_STYLES['open']['buy']
                    text = f'{comment} | +{deal[4]}'

                else:
                    styles = consts.MARKER_STYLES['open']['sell']
                    text = f'{comment} | -{deal[4]}'

                marker = {
                    'time': deal[2] * 0.001,
                    'text': text,
                    **styles
                }
                result.append(marker)
                
            return result

        for index, deal in enumerate(completed_deals):
            if deals_count > 0:
                prev_deal = completed_deals[index - 1]

                if prev_deal[3] != deal[3]:
                    code = prev_deal[1] - (prev_deal[1] % 100)
                    n_deal = int(prev_deal[1] % 100)
                    comment = (
                        f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                        (f' | #{n_deal}' if n_deal > 0 else '')
                    )

                    if prev_deal[0] == 0:
                        styles = consts.MARKER_STYLES['open']['buy']
                        text = f'{comment} | +{position_size}'
                    else:
                        styles = consts.MARKER_STYLES['open']['sell']
                        text = f'{comment} | -{position_size}'

                    marker = {
                        'time': prev_deal[3] * 0.001,
                        'text': text,
                        **styles
                    }
                    result.insert(len(result) - deals_count, marker)

                    position_size = Decimal('0.0')
                    deals_count = 0

            code = deal[2] - (deal[2] % 100)
            n_deal = int(deal[2] % 100)
            comment = (
                f'{consts.CLOSE_SIGNAL_CODES[code]}' +
                (f' | #{n_deal}' if n_deal > 0 else '')
            )

            if deal[0] == 0:
                styles = consts.MARKER_STYLES['close']['sell']
                text = f'{comment} | -{deal[7]}'
            else:
                styles = consts.MARKER_STYLES['close']['buy']
                text = f'{comment} | +{deal[7]}'

            marker = {
                'time': deal[4] * 0.001,
                'text': text,
                **styles
            }
            result.append(marker)

            position_size += Decimal(str(deal[7]))
            deals_count += 1

        last_deal = completed_deals[-1]

        for deal in open_deals:
            if deal[2] == last_deal[3]:
                position_size += Decimal(str(deal[4]))

        code = last_deal[1] - (last_deal[1] % 100)
        n_deal = int(last_deal[1] % 100)
        comment = (
            f'{consts.ENTRY_SIGNAL_CODES[code]}' +
            (f' | #{n_deal}' if n_deal > 0 else '')
        )

        if last_deal[0] == 0:
            styles = consts.MARKER_STYLES['open']['buy']
            text = f'{comment} | +{position_size}'
        else:
            styles = consts.MARKER_STYLES['open']['sell']
            text = f'{comment} | -{position_size}'

        marker = {
            'time': last_deal[3] * 0.001,
            'text': text,
            **styles
        }
        result.insert(len(result) - deals_count, marker)

        for deal in open_deals:
            if deal[2] != last_deal[3]:
                code = deal[1] - (deal[1] % 100)
                n_deal = int(deal[1] % 100)
                comment = (
                    f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                    (f' | #{n_deal}' if n_deal > 0 else '')
                )

                if deal[0] == 0:
                    styles = consts.MARKER_STYLES['open']['buy']
                    text = f'{comment} | +{deal[4]}'
                else:
                    styles = consts.MARKER_STYLES['open']['sell']
                    text = f'{comment} | -{deal[4]}'

                marker = {
                    'time': deal[2] * 0.001,
                    'text': text,
                    **styles
                }
                result.append(marker)

        return sorted(result, key=lambda x: x['time'])

    @staticmethod
    def _format_overview(
        completed_deals_log: np.ndarray,
        equity: np.ndarray,
        metrics: list
    ) -> dict:
        if not completed_deals_log.size:
            return {'metrics': [], 'equity': []}

        metrics_dict = {m['title']: m['all'] for m in metrics}
        formatted_metrics = []

        for title in consts.OVERVIEW_METRICS:
            target_metric = metrics_dict.get(title, [])
            suffixes = consts.METRIC_SUFFIXES.get(title, [])

            for i, value in enumerate(target_metric):
                suffix = suffixes[i] if i < len(suffixes) else ''
                formatted_metrics.append(f'{value}{suffix}')

        timestamps = completed_deals_log[4::13] * 0.001
        values = adjust_vectorized(equity, 0.01)

        formatted_equity = []
        used_timestamps = set()

        for t, v in zip(timestamps, values):
            adjusted_time = t

            while adjusted_time in used_timestamps:
                adjusted_time += 1

            used_timestamps.add(adjusted_time)
            formatted_equity.append({'time': adjusted_time, 'value': v})

        return {
            'metrics': formatted_metrics,
            'equity': formatted_equity
        }

    @staticmethod
    def _format_metrics(metrics: list) -> list:
        if len(metrics) == 0: return []

        result = []

        for metric in metrics:
            title = metric['title']
            suffixes = consts.METRIC_SUFFIXES.get(title, [])

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
    def _format_trades(
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray
    ) -> list:
        if not completed_deals_log.size and not open_deals_log.size:
            return []
        
        completed_deals = completed_deals_log.reshape((-1, 13))[:, :12]
        result = []

        for num, deal in enumerate(completed_deals, 1):
            code = deal[1] - (deal[1] % 100)
            n_deal = int(deal[1] % 100)
            entry_signal = (
                f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                (f' | #{n_deal}' if n_deal > 0 else '')
            )

            code = deal[2] - (deal[2] % 100)
            n_deal = int(deal[2] % 100)
            exit_signal = (
                f'{consts.CLOSE_SIGNAL_CODES[code]}' +
                (f' | #{n_deal}' if n_deal > 0 else '')
            )

            formatted = [
                str(num),
                consts.TRADE_TYPE_LABELS[deal[0]][1],
                consts.TRADE_TYPE_LABELS[deal[0]][0],
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

        open_deals = open_deals_log.reshape((-1, 5))
        mask = ~np.isnan(open_deals).any(axis=1)
        open_deals = open_deals[mask]

        for num, deal in enumerate(open_deals, num + 1):
            code = deal[1] - (deal[1] % 100)
            n_deal = int(deal[1] % 100)
            entry_signal = (
                f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                (f' | #{n_deal}' if n_deal > 0 else '')
            )

            formatted = [
                str(num),
                consts.TRADE_TYPE_LABELS[deal[0]][1],
                consts.TRADE_TYPE_LABELS[deal[0]][0],
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