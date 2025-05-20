from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal

import numpy as np

from src.core.enums import Mode
from .deal_keywords import DealKeywords


class DataFormatter:
    def __init__(self, mode: str, data_to_format: dict) -> None:
        self.mode = mode
        self.data_to_format = data_to_format

        self.main_data = {}
        self.lite_data = {}

    def format(self) -> None:
        for id, data in self.data_to_format.items():
            self.format_strategy_data(id, data)

    def format_strategy_data(self, id: str, data: dict) -> None:
        self.main_data[id] = {}
        self.main_data[id]['chartData'] = {
            'name': '-'.join(
                word.capitalize()
                for word in data['name'].split('_')
            ),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'market': data['market'].value,
            'interval': data['interval'],
            'mintick': data['p_precision'],
            'klines': self._format_klines(data['klines']),
            'indicators': self._format_indicators(
                data['klines'],
                data['instance'].indicators
            ),
            'markers': self._format_deal_markers(
                data['instance'].completed_deals_log,
                data['instance'].open_deals_log
            )
        }

        if self.mode is Mode.TESTING:
            self.main_data[id]['reportData'] = {
                'equity': self._format_equity(data['equity']),
                'metrics': data['metrics'],
                'completedDealsLog': self._format_completed_deals(
                    data['instance'].completed_deals_log
                ),
                'openDealsLog': self._format_open_deals(
                    data['instance'].open_deals_log
                )
            }

        self.lite_data[id] = {
            'name': '-'.join(
                word.capitalize()
                for word in data['name'].split('_')
            ),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'market': data['market'].value,
            'interval': data['interval'],
            'mintick': data['p_precision'],
            'params': data['params']
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
                marker = {
                    'time': deal[2] / 1000,
                    'position': 'belowBar' if deal[0] == 0 else 'aboveBar',
                    'color': '#2962ff' if deal[0] == 0 else '#ff1744',
                    'shape': 'arrowUp' if deal[0] == 0 else 'arrowDown',
                    'text': (
                        f'{DealKeywords.entry_signals[deal[1]]} '
                        f'{" +" if deal[0] == 0 else ' -'}{deal[4]}'
                    )
                }
                result.append(marker)
                
            return result

        for index, deal in enumerate(completed_deals):
            if deals_count > 0:
                prev_deal = completed_deals[index - 1]

                if prev_deal[3] != deal[3]:
                    marker = {
                        'time': prev_deal[3] / 1000,
                        'position': 'belowBar'
                            if prev_deal[0] == 0 else 'aboveBar',
                        'color': '#2962ff'
                            if prev_deal[0] == 0 else '#ff1744',
                        'shape': 'arrowUp'
                            if prev_deal[0] == 0 else 'arrowDown',
                        'text': (
                            f'{DealKeywords.entry_signals[prev_deal[1]]} '
                            f'{" +" if prev_deal[0] == 0 else ' -'}'
                            f'{position_size}'
                        )
                    }
                    result.insert(len(result) - deals_count, marker)

                    position_size = Decimal('0.0')
                    deals_count = 0

            marker = {
                'time': deal[4] / 1000,
                'position': 'aboveBar' if deal[0] == 0 else 'belowBar',
                'color': '#d500f9',
                'shape': 'arrowDown' if deal[0] == 0 else 'arrowUp',
                'text': (
                    f'{DealKeywords.exit_signals[deal[2]]} '
                    f'{" -" if deal[0] == 0 else ' +'}{deal[7]}'
                )
            }
            result.append(marker)

            position_size += Decimal(str(deal[7]))
            deals_count += 1

        last_deal = completed_deals[-1]

        for deal in open_deals:
            if deal[2] == last_deal[3]:
                position_size += Decimal(str(deal[4]))

        marker = {
            'time': last_deal[3] / 1000,
            'position': 'belowBar' 
                if last_deal[0] == 0 else 'aboveBar',
            'color': '#2962ff' 
                if last_deal[0] == 0 else '#ff1744',
            'shape': 'arrowUp' 
                if last_deal[0] == 0 else 'arrowDown',
            'text': (
                f'{DealKeywords.entry_signals[last_deal[1]]} '
                f'{" +" if last_deal[0] == 0 else ' -'}{position_size}'
            )
        }
        result.insert(len(result) - deals_count, marker)

        for deal in open_deals:
            if deal[2] != last_deal[3]:
                marker = {
                    'time': deal[2] / 1000,
                    'position': 'belowBar' if deal[0] == 0 else 'aboveBar',
                    'color': '#2962ff' if deal[0] == 0 else '#ff1744',
                    'shape': 'arrowUp' if deal[0] == 0 else 'arrowDown',
                    'text': (
                        f'{DealKeywords.entry_signals[deal[1]]} '
                        f'{" +" if deal[0] == 0 else ' -'}{deal[4]}'
                    )
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

    def _format_completed_deals(self, completed_deals_log: np.ndarray) -> list:
        result = completed_deals_log.reshape((-1, 13)).tolist()

        for deal in result:
            deal[0] = DealKeywords.deal_types[deal[0]]
            deal[1] = DealKeywords.entry_signals[deal[1]]
            deal[2] = DealKeywords.exit_signals[deal[2]]
            deal[3] = datetime.fromtimestamp(
                deal[3] / 1000, tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            deal[4] = datetime.fromtimestamp(
                deal[4] / 1000, tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')

        return result

    def _format_open_deals(self, open_deals_log: np.ndarray) -> list:
        result = list(
            filter(
                lambda deal: not np.isnan(deal[0]),
                open_deals_log.reshape((-1, 5)).tolist()
            )
        )

        for deal in result:
            deal[0] = DealKeywords.deal_types[deal[0]]
            deal[1] = DealKeywords.entry_signals[deal[1]]
            deal[2] = datetime.fromtimestamp(
                deal[2] / 1000, tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')

        return result