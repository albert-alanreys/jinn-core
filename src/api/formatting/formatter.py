from datetime import datetime, timezone
from decimal import Decimal

import numpy as np

from src.core.utils.colors import decode_rgb
from src.core.utils.rounding import adjust
from . import constants as consts


class Formatter:
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

    @staticmethod
    def format_details(strategy_context: dict) -> dict:
        result = {}

        result['chart'] = {
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
            'markers': Formatter._format_deal_markers(
                strategy_context['instance'].completed_deals_log,
                strategy_context['instance'].open_deals_log
            )
        }

        result['report'] = {
            'equity': Formatter._format_equity(
                strategy_context['stats']['equity']
            ),
            'metrics': strategy_context['stats']['metrics'],
            'deals': Formatter._format_deals_log(
                strategy_context['instance'].completed_deals_log,
                strategy_context['instance'].open_deals_log
            )
        }

        return result

    @staticmethod
    def _format_klines(klines: np.ndarray) -> list:
        result = [
            {
                'time': kline[0] / 1000,
                'open': kline[1],
                'high': kline[2],
                'low': kline[3],
                'close': kline[4],
            } for kline in klines.tolist()
        ]
        return result

    @staticmethod
    def _format_indicators(market_data: dict, indicators: dict) -> dict:
        klines = market_data['klines']
        p_precision = market_data['p_precision']
        
        result = {}

        for name in indicators.keys():
            values = indicators[name]['values']
            colors = indicators[name].get('colors')
            points = []

            for i in range(klines.shape[0]):
                timestamp = int(klines[i][0] / 1000)
                value = adjust(values[i], p_precision)
                color = None

                if np.isnan(values[i]):
                    value = '∅'
                    color = 't'

                if colors is not None:
                    color = 't'

                    if not np.isnan(colors[i]):
                        r, g, b = decode_rgb(colors[i])
                        color = f'rgb({r}, {g}, {b})'

                point = {
                    'time': timestamp,
                    'value': value
                }

                if color is not None:
                    point['color'] = color
 
                points.append(point)

            if name not in result:
                result[name] = {}

            result[name]['options'] = indicators[name]['options']
            result[name]['values'] = points

        return result

    @staticmethod
    def _format_deal_markers(
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray
    ) -> list:
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
                    'time': deal[2] / 1000,
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
                        'time': prev_deal[3] / 1000,
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
                'time': deal[4] / 1000,
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
            'time': last_deal[3] / 1000,
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
                    'time': deal[2] / 1000,
                    'text': text,
                    **styles
                }
                result.append(marker)

        return sorted(result, key=lambda x: x['time'])

    @staticmethod
    def _format_equity(equity: list) -> list:
        result = [
            {
                'time': i + 1,
                'value': value,
            } for i, value in enumerate(equity)
        ]
        return result

    @staticmethod
    def _format_deals_log(
        closed_deals: np.ndarray,
        open_deals: np.ndarray
    ) -> list:
        closed = closed_deals.reshape((-1, 13))[:, :12]
        formatted_closed = []

        for deal in closed:
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
                consts.DEAL_TYPES[deal[0]],
                entry_signal,
                exit_signal,
                datetime.fromtimestamp(
                    timestamp=deal[3] / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M'),
                datetime.fromtimestamp(
                    timestamp=deal[4] / 1000,
                    tz=timezone.utc
                ).strftime('%Y/%m/%d %H:%M'),
                *deal[5:12].tolist()
            ]
            formatted_closed.append(formatted)

        reshaped_open_deals = open_deals.reshape((-1, 5))
        mask = ~np.isnan(reshaped_open_deals).any(axis=1)
        reshaped_open_deals = reshaped_open_deals[mask]
        formatted_open = []

        for deal in reshaped_open_deals:
            code = deal[1] - (deal[1] % 100)
            n_deal = int(deal[1] % 100)
            entry_signal = (
                f'{consts.ENTRY_SIGNAL_CODES[code]}' +
                (f' | #{n_deal}' if n_deal > 0 else '')
            )

            formatted = [None] * 12
            formatted[0] = consts.DEAL_TYPES[deal[0]]
            formatted[1] = entry_signal
            formatted[3] = datetime.fromtimestamp(
                timestamp=deal[2]/1000,
                tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            formatted[5] = float(deal[3])
            formatted[7] = float(deal[4])
            formatted_open.append(formatted)

        return formatted_closed + formatted_open