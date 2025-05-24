from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

import numpy as np

from src.core.enums import Mode
from . import deal_constants as consts


class DataFormatter:
    MARKER_STYLES = {
        'open': {
            'buy': {
                'position': 'belowBar',
                'color': '#2962ff',
                'shape': 'arrowUp'
            },
            'sell': {
                'position': 'aboveBar',
                'color': '#ff1744',
                'shape': 'arrowDown'
            }
        },
        'close': {
            'sell': {
                'position': 'aboveBar',
                'color': '#d500f9',
                'shape': 'arrowDown'
            },
            'buy': {
                'position': 'belowBar',
                'color': '#d500f9',
                'shape': 'arrowUp'
            }
        }
    }

    def __init__(self, strategy_states: dict, mode: str) -> None:
        self.strategy_states = strategy_states
        self.mode = mode

        self.main_data = {}
        self.lite_data = {}

    def format(self) -> None:
        for id, state in self.strategy_states.items():
            self.format_strategy_states(id, state)

    def format_strategy_states(
            self,
            strategy_id: str,
            strategy_state: dict
        ) -> None:
        self.main_data[strategy_id] = {}
        self.main_data[strategy_id]['chartData'] = {
            'name': '-'.join(
                word.capitalize()
                for word in strategy_state['name'].split('_')
            ),
            'exchange': strategy_state['client'].EXCHANGE,
            'symbol': strategy_state['market_data']['symbol'],
            'market': strategy_state['market_data']['market'].value,
            'interval': strategy_state['market_data']['interval'],
            'mintick': strategy_state['market_data']['p_precision'],
            'klines': self._format_klines(
                strategy_state['market_data']['klines']
            ),
            'indicators': self._format_indicators(
                strategy_state['market_data']['klines'],
                strategy_state['instance'].indicators
            ),
            'markers': self._format_deal_markers(
                strategy_state['instance'].completed_deals_log,
                strategy_state['instance'].open_deals_log
            )
        }

        if self.mode is Mode.TESTING:
            self.main_data[strategy_id]['reportData'] = {
                'equity': self._format_equity(strategy_state['equity']),
                'metrics': strategy_state['metrics'],
                'dealsLog': self._format_deals_log(
                    strategy_state['instance'].completed_deals_log,
                    strategy_state['instance'].open_deals_log
                )
            }

        self.lite_data[strategy_id] = {
            'name': '-'.join(
                word.capitalize()
                for word in strategy_state['name'].split('_')
            ),
            'exchange': strategy_state['client'].EXCHANGE,
            'symbol': strategy_state['market_data']['symbol'],
            'market': strategy_state['market_data']['market'].value,
            'interval': strategy_state['market_data']['interval'],
            'mintick': strategy_state['market_data']['p_precision'],
            'params': {
                k: v for k, v in strategy_state['instance'].params.items()
                if k != 'feeds'
            }
        }

    def _format_klines(self, klines: np.ndarray) -> list:
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

    def _format_indicators(
        self,
        klines: np.ndarray,
        indicators: dict
    ) -> dict:
        result = deepcopy(indicators)

        for name in result.keys():
            raw_values = result[name]['values'].tolist()
            line_data = []

            for i in range(klines.shape[0]):
                timestamp = klines[i][0] / 1000

                if not np.isnan(raw_values[i]):
                    point = {
                        'time': timestamp,
                        'value': raw_values[i]
                    }
                else:
                    point = {
                        'time': timestamp,
                        'value': '∅',
                        'color': 't'
                    }

                line_data.append(point)

            result[name]['values'] = line_data

        return result

    def _format_deal_markers(
        self,
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
                    styles = self.MARKER_STYLES['open']['buy']
                    text = f'{comment} | +{deal[4]}'

                else:
                    styles = self.MARKER_STYLES['open']['sell']
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
                        styles = self.MARKER_STYLES['open']['buy']
                        text = f'{comment} | +{position_size}'
                    else:
                        styles = self.MARKER_STYLES['open']['sell']
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
                styles = self.MARKER_STYLES['close']['sell']
                text = f'{comment} | -{deal[7]}'
            else:
                styles = self.MARKER_STYLES['close']['buy']
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
            styles = self.MARKER_STYLES['open']['buy']
            text = f'{comment} | +{position_size}'
        else:
            styles = self.MARKER_STYLES['open']['sell']
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
                    styles = self.MARKER_STYLES['open']['buy']
                    text = f'{comment} | +{deal[4]}'
                else:
                    styles = self.MARKER_STYLES['open']['sell']
                    text = f'{comment} | -{deal[4]}'

                marker = {
                    'time': deal[2] / 1000,
                    'text': text,
                    **styles
                }
                result.append(marker)

        return sorted(result, key=lambda x: x['time'])

    def _format_equity(self, equity: np.ndarray) -> list:
        result = [
            {
                'time': i + 1,
                'value': value,
            } for i, value in enumerate(equity.tolist())
        ]
        return result

    def _format_deals_log(
        self,
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