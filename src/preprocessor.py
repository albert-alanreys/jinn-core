import datetime as dt

import numpy as np


class Preprocessor:
    @staticmethod
    def get_klines(klines):
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
    def get_indicators(klines, indicators):
        klines = klines.tolist()

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
            completed_deals_log, open_deals_log,
            entry_signal_keywords, exit_signal_keywords, precision
    ):
        completed_deals_log = completed_deals_log.tolist()
        open_deals_log = open_deals_log.tolist()
        result = []
        deal_type = np.nan
        entry_signal = np.nan
        position_size = 0
        exits = 0

        if len(completed_deals_log) == 0:
            if np.isnan(open_deals_log[0]):
                return []
            
            result.append(
                {
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
                },
            )
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
                        },
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
            result.append(
                {
                    "time": deal[4] / 1000,
                    "position": 'aboveBar' 
                        if deal[0] == 0 else 'belowBar',
                    "color": '#d500f9',
                    "shape": 'arrowDown'
                        if deal[0] == 0 else 'arrowUp',
                    "text": (exit_signal_keywords[deal[2]] +
                        (' -' if deal[0] == 0 else ' +') +
                        str(deal[7]))
                },
            )

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
    def get_equity(equity):
        result = [
            {
                "time": i + 1,
                "value": value,
            } for i, value in enumerate(equity.tolist())
        ]
        return result

    @staticmethod
    def get_completed_deals_log(
            completed_deals_log, deal_type_keywords,
            entry_signal_keywords, exit_signal_keywords
    ):
        completed_deals_log = completed_deals_log.tolist()

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
            open_deals_log, deal_type_keywords, entry_signal_keywords
    ):
        if np.isnan(open_deals_log[0]):
            return []

        open_deals_log = open_deals_log.tolist()
        open_deals_log[0] = deal_type_keywords[open_deals_log[0]]
        open_deals_log[1] = entry_signal_keywords[open_deals_log[1]]
        open_deals_log[2] = dt.datetime.fromtimestamp(
            open_deals_log[2] / 1000, tz=dt.timezone.utc
        ).strftime('%Y/%m/%d %H:%M')
        return open_deals_log