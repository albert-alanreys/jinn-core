import ast
import warnings
import datetime as dt
from copy import deepcopy

import numpy as np

from src.controller.deal_keywords import DealKeywords


class Preprocessor:
    def __init__(
        self,
        mode: str,
        strategies: dict[str, dict]
    ) -> None:
        self.mode = mode
        self.strategies = strategies
        self.main_data = {}
        self.lite_data = {}

        for id, data in self.strategies.items():
            data['instance'].start(data['client'])
            self.prepare_data(id, data)

    def update_strategy(
        self,
        id: str,
        parameter_name: str,
        new_value: int | float
    ) -> None:
        try:
            parameters = self.strategies[id]['parameters']
            old_value = parameters[parameter_name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float) and isinstance(new_value, int):
                    new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise ValueError()

            parameters[parameter_name] = new_value
            strategy_instance = (
                self.strategies[id]['instance'].__class__(
                    all_parameters=list(parameters.values())
                )
            )
            self.strategies[id]['instance'] = strategy_instance
            self.strategies[id]['instance'].start(
                self.strategies[id]['client']
            )
            self.prepare_data(id, self.strategies[id])
        except Exception:
            raise ValueError()

    def prepare_data(
        self,
        id: str,
        data: dict[str, dict]
    ) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            equity = data['instance'].get_equity(
                data['instance'].initial_capital,
                data['instance'].completed_deals_log
            )
            metrics = data['instance'].get_metrics(
                data['instance'].initial_capital,
                data['instance'].completed_deals_log
            )

        main_data = {}
        main_data['chartData'] = {
            'name': data['name'].capitalize().replace('_', '-'),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'interval': data['interval'],
            'mintick': data['mintick'],
            'klines': self.get_klines(
                data['client'].price_data
            ),
            'indicators': self.get_indicators(
                data['client'].price_data,
                data['instance'].indicators
            ),
            'markers': self.get_deals(
                data['instance'].completed_deals_log,
                data['instance'].open_deals_log,
                DealKeywords.entry_signals,
                DealKeywords.exit_signals,
                data['instance'].qty_precision
            )
        }

        if self.mode == 'testing':
            main_data['reportData'] = {
                'equity': self.get_equity(equity),
                'metrics': metrics,
                'completedDealsLog': self.get_completed_deals_log(
                    data['instance'].completed_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                ),
                'openDealsLog': self.get_open_deals_log(
                    data['instance'].open_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals
                )
            }

        lite_data = {
            'name': data['name'].capitalize().replace('_', '-'),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'interval': data['interval'],
            'mintick': data['mintick'],
            'parameters': data['parameters']
        }
        self.main_data[id] = main_data
        self.lite_data[id] = lite_data

    @staticmethod
    def get_klines(klines: np.ndarray) -> list[dict]:
        result = [
            {
                "time": kline[0] / 1000,
                "open": kline[1],
                "high": kline[2],
                "low": kline[3],
                "close": kline[4],
            } for kline in klines.tolist()
        ]
        return result

    @staticmethod
    def get_indicators(klines: np.ndarray, indicators: dict) -> dict:
        klines = klines.tolist()
        indicators = deepcopy(indicators)

        for key in indicators.keys():
            values = indicators[key]['values'].tolist()
            options = indicators[key]['options']
            indicator = []

            for i in range(len(klines)):
                if not np.isnan(values[i]):
                    indicator.append({
                        "time": klines[i][0] / 1000,
                        "value": values[i],
                        "color": options["color"],
                    })

                    if i < len(klines) - 1:
                        if np.isnan(values[i + 1]):
                            indicator[-1]["color"] = "transparent"
                else:
                    indicator.append({
                        "time": klines[i][0] / 1000,
                        "value": klines[i][1],
                        "color": "transparent",
                    })

            indicators[key]['values'] = indicator

        return indicators

    @staticmethod
    def get_deals(
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray,
        entry_signal_keywords: DealKeywords,
        exit_signal_keywords: DealKeywords,
        precision: float
    ) -> list[dict]:
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
                "time": open_deals_log[2] / 1000,
                "position": 'belowBar' 
                    if open_deals_log[0] == 0 else 'aboveBar',
                "color": '#2962ff' 
                    if open_deals_log[0] == 0 else '#ff1744',
                "shape": 'arrowUp' 
                    if open_deals_log[0] == 0 else 'arrowDown',
                "text": (entry_signal_keywords[open_deals_log[1]] +
                    (' +' if open_deals_log[0] == 0 else ' -') +
                    str(open_deals_log[4]))
            })
            return result

        for deal in completed_deals_log:
            if exits > 0:
                if entry_date != deal[3]:
                    position_size = round(
                        round(position_size / precision) * precision,
                        8
                    )
                    result.insert(
                        len(result) - exits,
                        {
                            "time": entry_date / 1000,
                            "position": 'belowBar' 
                                if deal_type == 0 else 'aboveBar',
                            "color": '#2962ff' 
                                if deal_type == 0 else '#ff1744',
                            "shape": 'arrowUp' 
                                if deal_type == 0 else 'arrowDown',
                            "text": (entry_signal_keywords[entry_signal] +
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
                "time": deal[4] / 1000,
                "position": 'aboveBar' 
                    if deal[0] == 0 else 'belowBar',
                "color": '#d500f9',
                "shape": 'arrowDown'
                    if deal[0] == 0 else 'arrowUp',
                "text": (exit_signal_keywords[deal[2]] +
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
                "time": deal[3] / 1000,
                "position": 'belowBar' 
                    if deal[0] == 0 else 'aboveBar',
                "color": '#2962ff' 
                    if deal[0] == 0 else '#ff1744',
                "shape": 'arrowUp' 
                    if deal[0] == 0 else 'arrowDown',
                "text": (entry_signal_keywords[deal[1]] +
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
                "time": open_deals_log[2] / 1000,
                "position": 'belowBar' 
                    if open_deals_log[0] == 0 else 'aboveBar',
                "color": '#2962ff' 
                    if open_deals_log[0] == 0 else '#ff1744',
                "shape": 'arrowUp' 
                    if open_deals_log[0] == 0 else 'arrowDown',
                "text": (entry_signal_keywords[open_deals_log[1]] +
                    (' +' if open_deals_log[0] == 0 else ' -') +
                    str(position_size))
            })

        return result

    @staticmethod
    def get_equity(equity: np.ndarray) -> list[dict]:
        result = [
            {
                "time": i + 1,
                "value": value,
            } for i, value in enumerate(equity.tolist())
        ]
        return result

    @staticmethod
    def get_completed_deals_log(
        completed_deals_log: np.ndarray,
        deal_type_keywords: DealKeywords,
        entry_signal_keywords: DealKeywords,
        exit_signal_keywords: DealKeywords
    ) -> list[list]:
        completed_deals_log = completed_deals_log.reshape((-1, 13)).tolist()

        for deal in completed_deals_log:
            deal[0] = deal_type_keywords[deal[0]]
            deal[1] = entry_signal_keywords[deal[1]]
            deal[2] = exit_signal_keywords[deal[2]]
            deal[3] = dt.datetime.fromtimestamp(
                deal[3] / 1000, tz=dt.timezone.utc
            ).strftime('%Y/%m/%d %H:%M')
            deal[4] = dt.datetime.fromtimestamp(
                deal[4] / 1000, tz=dt.timezone.utc
            ).strftime('%Y/%m/%d %H:%M')

        return completed_deals_log

    @staticmethod
    def get_open_deals_log(
        open_deals_log: np.ndarray,
        deal_type_keywords: DealKeywords,
        entry_signal_keywords: DealKeywords
    ) -> list:
        if np.isnan(open_deals_log[0]):
            return []

        open_deals_log = open_deals_log.tolist()
        open_deals_log[0] = deal_type_keywords[open_deals_log[0]]
        open_deals_log[1] = entry_signal_keywords[open_deals_log[1]]
        open_deals_log[2] = dt.datetime.fromtimestamp(
            open_deals_log[2] / 1000, tz=dt.timezone.utc
        ).strftime('%Y/%m/%d %H:%M')
        return open_deals_log