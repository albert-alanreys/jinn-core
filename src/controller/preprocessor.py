import ast
from copy import deepcopy
from datetime import datetime, timezone

import numpy as np

from src.model.enums import Mode
from src.controller.deal_keywords import DealKeywords


class Preprocessor:
    def __init__(self, mode: str, data_to_process: dict) -> None:
        self.mode = mode
        self.data_to_process = data_to_process[1]

        if self.mode is Mode.TESTING:
            self.tester = data_to_process[0]

        self.main_data = {}
        self.lite_data = {}

    def process(self) -> None:
        for key, values in self.data_to_process.items():
            self.prepare_strategy_data(key, values)

    def update_strategy(
        self,
        strategy_id: str,
        parameter_name: str,
        new_value: int | float
    ) -> None:
        try:
            parameters = self.data_to_process[strategy_id]['parameters']
            old_value = parameters[parameter_name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float):
                    if isinstance(new_value, int):
                        new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise ValueError()

            parameters[parameter_name] = new_value
            instance = (
                self.data_to_process[strategy_id]['instance'].__class__(
                    all_params=list(parameters.values())
                )
            )
            self.data_to_process[strategy_id]['instance'] = instance

            equity, metrics = self.tester.calculate_strategy(
                self.data_to_process[strategy_id]
            )
            self.data_to_process[strategy_id]['equity'] = equity
            self.data_to_process[strategy_id]['metrics'] = metrics
            self.prepare_strategy_data(
                strategy_id, self.data_to_process[strategy_id]
            )
        except ValueError:
            raise ValueError()
        except KeyError:
            raise KeyError()

    def prepare_strategy_data(
        self,
        strategy_id: str,
        strategy_data: dict
    ) -> None:
        self.main_data[strategy_id] = {}
        self.main_data[strategy_id]['chartData'] = {
            'name': strategy_data['name'].capitalize().replace('_', '-'),
            'exchange': strategy_data['exchange'],
            'symbol': strategy_data['symbol'],
            'interval': strategy_data['interval'],
            'mintick': strategy_data['p_precision'],
            'klines': self.get_klines(strategy_data['klines']),
            'indicators': self.get_indicators(
                strategy_data['klines'],
                strategy_data['instance'].indicators
            ),
            'markers': self.get_deals(
                strategy_data['instance'].completed_deals_log,
                strategy_data['instance'].open_deals_log,
                strategy_data['q_precision']
            )
        }

        if self.mode is Mode.TESTING:
            self.main_data[strategy_id]['reportData'] = {
                'equity': self.get_equity(strategy_data['equity']),
                'metrics': strategy_data['metrics'],
                'completedDealsLog': self.get_completed_deals_log(
                    strategy_data['instance'].completed_deals_log
                ),
                'openDealsLog': self.get_open_deals_log(
                    strategy_data['instance'].open_deals_log
                )
            }

        self.lite_data[strategy_id] = {
            'name': strategy_data['name'].capitalize().replace('_', '-'),
            'exchange': strategy_data['exchange'],
            'symbol': strategy_data['symbol'],
            'interval': strategy_data['interval'],
            'mintick': strategy_data['p_precision'],
            'parameters': strategy_data['parameters']
        }

    def get_klines(self, klines: np.ndarray) -> list:
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

    def get_indicators(self, klines: np.ndarray, indicators: dict) -> dict:
        klines = klines.tolist()
        indicators = deepcopy(indicators)

        for key in indicators.keys():
            values = indicators[key]['values'].tolist()
            options = indicators[key]['options']
            indicator = []

            for i in range(len(klines)):
                if not np.isnan(values[i]):
                    indicator.append({
                        'time': klines[i][0] / 1000,
                        'value': values[i],
                        'color': options['color'],
                    })

                    if i < len(klines) - 1:
                        if np.isnan(values[i + 1]):
                            indicator[-1]['color'] = 'transparent'
                else:
                    indicator.append({
                        'time': klines[i][0] / 1000,
                        'value': klines[i][1],
                        'color': 'transparent',
                    })

            indicators[key]['values'] = indicator

        return indicators

    def get_deals(
        self,
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray,
        precision: float
    ) -> list:
        completed_deals_log = completed_deals_log.reshape((-1, 13)).tolist()
        open_deals_log = open_deals_log.tolist()
        result = []
        deal_type = np.nan
        entry_signal = np.nan
        position_size = 0
        exits = 0

        if len(completed_deals_log) == 0:
            if np.isnan(open_deals_log[0]):
                return []
            
            result.append({
                'time': open_deals_log[2] / 1000,
                'position': 'belowBar' 
                    if open_deals_log[0] == 0 else 'aboveBar',
                'color': '#2962ff' 
                    if open_deals_log[0] == 0 else '#ff1744',
                'shape': 'arrowUp' 
                    if open_deals_log[0] == 0 else 'arrowDown',
                'text': (DealKeywords.entry_signals[open_deals_log[1]] +
                    (' +' if open_deals_log[0] == 0 else ' -') +
                    str(open_deals_log[4]))
            })
            return result

        for deal in completed_deals_log:
            if exits > 0 and entry_date != deal[3]:
                position_size = round(
                    round(position_size / precision) * precision,
                    8
                )
                result.insert(
                    len(result) - exits,
                    {
                        'time': entry_date / 1000,
                        'position': 'belowBar' 
                            if deal_type == 0 else 'aboveBar',
                        'color': '#2962ff' 
                            if deal_type == 0 else '#ff1744',
                        'shape': 'arrowUp' 
                            if deal_type == 0 else 'arrowDown',
                        'text': (DealKeywords.entry_signals[entry_signal] +
                            (' +' if deal_type == 0 else ' -') +
                            str(position_size))
                    }
                )
                deal_type = np.nan
                entry_signal = np.nan
                position_size = 0
                exits = 0

            deal_type = deal[0]
            entry_signal = deal[1]
            entry_date = deal[3]
            position_size += deal[7]
            exits += 1
            result.append({
                'time': deal[4] / 1000,
                'position': 'aboveBar' 
                    if deal[0] == 0 else 'belowBar',
                'color': '#d500f9',
                'shape': 'arrowDown'
                    if deal[0] == 0 else 'arrowUp',
                'text': (DealKeywords.exit_signals[deal[2]] +
                    (' -' if deal[0] == 0 else ' +') +
                    str(deal[7]))
            })

        if not np.isnan(open_deals_log[0]) and open_deals_log[2] == deal[3]:
            position_size += open_deals_log[4]

        position_size = round(
            round(position_size / precision) * precision,
            8
        )
        result.insert(
            len(result) - exits,
            {
                'time': deal[3] / 1000,
                'position': 'belowBar' 
                    if deal[0] == 0 else 'aboveBar',
                'color': '#2962ff' 
                    if deal[0] == 0 else '#ff1744',
                'shape': 'arrowUp' 
                    if deal[0] == 0 else 'arrowDown',
                'text': (DealKeywords.entry_signals[deal[1]] +
                    (' +' if deal[0] == 0 else ' -') +
                    str(position_size))
            }
        )

        if not np.isnan(open_deals_log[0]) and open_deals_log[2] != deal[3]:
            position_size = round(
                round(open_deals_log[4] / precision) * precision,
                8
            )
            result.append({
                'time': open_deals_log[2] / 1000,
                'position': 'belowBar' 
                    if open_deals_log[0] == 0 else 'aboveBar',
                'color': '#2962ff' 
                    if open_deals_log[0] == 0 else '#ff1744',
                'shape': 'arrowUp' 
                    if open_deals_log[0] == 0 else 'arrowDown',
                'text': (DealKeywords.entry_signals[open_deals_log[1]] +
                    (' +' if open_deals_log[0] == 0 else ' -') +
                    str(position_size))
            })

        return result

    def get_equity(self, equity: np.ndarray) -> list:
        result = [
            {
                'time': i + 1,
                'value': value,
            } for i, value in enumerate(equity.tolist())
        ]
        return result

    def get_completed_deals_log(
        self,
        completed_deals_log: np.ndarray
    ) -> list:
        completed_deals_log = completed_deals_log.reshape((-1, 13)).tolist()

        for deal in completed_deals_log:
            deal[0] = DealKeywords.deal_types[deal[0]]
            deal[1] = DealKeywords.entry_signals[deal[1]]
            deal[2] = DealKeywords.exit_signals[deal[2]]
            deal[3] = datetime.fromtimestamp(
                deal[3] / 1000, tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            deal[4] = datetime.fromtimestamp(
                deal[4] / 1000, tz=timezone.utc
            ).strftime('%Y/%m/%d %H:%M')

        return completed_deals_log

    def get_open_deals_log(self, open_deals_log: np.ndarray) -> list:
        if np.isnan(open_deals_log[0]):
            return []

        open_deals_log = open_deals_log.tolist()
        open_deals_log[0] = DealKeywords.deal_types[open_deals_log[0]]
        open_deals_log[1] = DealKeywords.entry_signals[open_deals_log[1]]
        open_deals_log[2] = datetime.fromtimestamp(
            open_deals_log[2] / 1000, tz=timezone.utc
        ).strftime('%Y/%m/%d %H:%M')
        
        return open_deals_log