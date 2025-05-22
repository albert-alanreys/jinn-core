import numpy as np
import numba as nb

import src.core.lib.ta as ta
from src.core.strategy.base_strategy import BaseStrategy


class Sandbox(BaseStrategy):
    # Strategy parameters
    # Names must be in double quotes

    # margin_type: 0 — 'ISOLATED', 1 — 'CROSSED'
    # order_size_type: 0 — "PERCENT", 1 — "CURRENCY"
    params = {
        "margin_type":  0,
        "initial_capital":  10000.0,
        "commission":  0.075,
        "order_size_type":  0,
        "order_size":  50,
        "leverage":  1,
        "entry_volume":  [10.0, 15.0, 25.0, 50.0],
        "entry_percent_2":  2.0,
        "entry_percent_3":  6.0,
        "entry_percent_4":  8.0,
        "take_profit":  1.0,
        "lookback":  1,
        "ma_length":  20,
        "mult":  2.0,
        "range_threshold":  30.0,
        "intervals": ["1d", "15m"]
    }

    # Parameters to be optimized and their possible values
    # Intervals are not subject to optimization
    opt_params = {
        'entry_volume': [
            [10.0, 15.0, 25.0, 50.0],
            [20.0, 20.0, 20.0, 40.0],
            [10.0, 10.0, 40.0, 40.0],
            [15.0, 15.0, 15.0, 55.0], 
            [5.0, 15.0, 30.0, 50.0],
            [25.0, 25.0, 25.0, 25.0],
            [10.0, 20.0, 30.0, 40.0],
            [40.0, 30.0, 20.0, 10.0],
            [50.0, 20.0, 20.0, 10.0],
            [10.0, 30.0, 10.0, 50.0], 
            [12.0, 18.0, 25.0, 45.0],
            [30.0, 25.0, 25.0, 20.0],
            [5.0, 25.0, 25.0, 45.0],
            [15.0, 25.0, 35.0, 25.0],
            [35.0, 35.0, 15.0, 15.0],
            [10.0, 40.0, 20.0, 30.0],
            [22.0, 22.0, 22.0, 34.0],
            [7.0, 13.0, 37.0, 43.0],
            [18.0, 18.0, 32.0, 32.0],
            [27.0, 23.0, 27.0, 23.0]
        ],
        'entry_percent_2': [i / 10 for i in range(20, 101)],
        'entry_percent_3': [i / 10 for i in range(50, 151)],
        'entry_percent_4': [i / 10 for i in range(100, 301)],
        'take_profit': [i / 10 for i in range(10, 201)],
        'lookback': [i for i in range(1, 21)],
        'ma_length': [i for i in range(10, 101)],
        'mult': [i / 10 for i in range(10, 31)],
        'range_threshold': [float(i) for i in range(10, 100)]
    }

    # For frontend
    indicator_options = {
        'EP #2': {'color': '#311b92'},
        'EP #3': {'color': '#311b92'},
        'EP #4': {'color': '#311b92'},
        'TP': {'color': '#4caf50'}
    }

    def __init__(self, client, all_params = None, opt_params = None) -> None:
        super().__init__(client, all_params=all_params, opt_params=opt_params)

    def start(self, market_data) -> None:
        self.open_deals_log = np.full((4, 5), np.nan)
        self.completed_deals_log = np.array([])
        self.position_size = np.nan
        self.entry_signal = np.nan
        self.entry_price = np.nan
        self.entry_date = np.nan
        self.deal_type = np.nan

        self.symbol = market_data['symbol']
        self.time = market_data['klines'][:, 0]
        self.open = market_data['klines'][:, 1]
        self.high = market_data['klines'][:, 2]
        self.low = market_data['klines'][:, 3]
        self.close = market_data['klines'][:, 4]
        self.p_precision = market_data['p_precision']
        self.q_precision = market_data['q_precision']

        self.equity = self.params['initial_capital']
        self.qty_entry = np.full(4, np.nan)
        self.entry_price_2 = np.full(self.time.shape[0], np.nan)
        self.entry_price_3 = np.full(self.time.shape[0], np.nan)
        self.entry_price_4 = np.full(self.time.shape[0], np.nan)
        self.take_price = np.full(self.time.shape[0], np.nan)
        self.liquidation_price = np.nan

        self.lowest = ta.lowest(
            source=np.roll(self.low, 1),
            length=self.params['lookback']
        )
        self.sma = ta.sma(
            source=(self.high - self.low), 
            length=self.params['ma_length']
        )

        self.alert_open_long = False
        self.alert_close_long = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.entry_price_2,
            self.entry_price_3,
            self.entry_price_4,
            self.take_price,
            self.alert_open_long,
            self.alert_close_long
        ) = self._calculate(
            self.params['initial_capital'],
            self.params['commission'],
            self.params['order_size_type'],
            self.params['order_size'],
            self.params['leverage'],
            self.params['entry_volume'],
            self.params['entry_percent_2'],
            self.params['entry_percent_3'],
            self.params['entry_percent_4'],
            self.params['take_profit'],
            self.params['mult'],
            self.params['range_threshold'],
            self.p_precision,
            self.q_precision,
            self.time,
            self.open,
            self.high,
            self.low,
            self.close,
            self.equity,
            self.completed_deals_log,
            self.open_deals_log,
            self.position_size,
            self.entry_signal,
            self.entry_price,
            self.entry_date,
            self.deal_type,
            self.liquidation_price,
            self.take_price,
            self.qty_entry,
            self.entry_price_2,
            self.entry_price_3,
            self.entry_price_4,
            self.lowest,
            self.sma,
            self.alert_open_long,
            self.alert_close_long
        )

        self.indicators = {
            'EP #2': {
                'options': self.indicator_options['EP #2'],
                'values': self.entry_price_2
            },
            'EP #3': {
                'options': self.indicator_options['EP #3'],
                'values': self.entry_price_3
            },
            'EP #4': {
                'options': self.indicator_options['EP #4'],
                'values': self.entry_price_4
            },
            'TP': {
                'options': self.indicator_options['TP'],
                'values': self.take_price
            }
        }

    @staticmethod
    @nb.jit(cache=True, nopython=True, nogil=True)
    def _calculate(
        initial_capital: float,
        commission: float,
        order_size_type: int,
        order_size: float,
        leverage: int,
        entry_volume: list,
        entry_percent_2: float,
        entry_percent_3: float,
        entry_percent_4: float,
        take_profit: float,
        mult: float,
        range_threshold: float,
        p_precision: float,
        q_precision: float,
        time: np.ndarray,
        open: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        equity: float,
        completed_deals_log: np.ndarray,
        open_deals_log: np.ndarray,
        position_size: float,
        entry_signal: float,
        entry_price: float,
        entry_date: float,
        deal_type: float,
        liquidation_price: float,
        take_price: np.ndarray,
        qty_entry: np.ndarray,
        entry_price_2: np.ndarray,
        entry_price_3: np.ndarray,
        entry_price_4: np.ndarray,
        lowest: np.ndarray,
        sma: np.ndarray,
        alert_open_long: bool,
        alert_close_long: bool
    ) -> tuple:
        def adjust(number: float, precision: float, digits: int = 8) -> float:
            return round(round(number / precision) * precision, digits)

        def update_log(
            log: np.ndarray,
            equity: float,
            commission: float,
            deal_type: float,
            entry_signal: float,
            exit_signal: float,
            entry_date: float,
            exit_date: float,
            entry_price: float,
            exit_price: float,
            position_size: float,
            initial_capital: float
        ) -> tuple[np.ndarray, float]:
            total_commission = round(
                (position_size * entry_price
                    * commission / 100) + (position_size
                    * exit_price * commission / 100),
                2
            )

            if deal_type == 0:
                pnl = round(
                    (exit_price - entry_price) * position_size
                        - total_commission,
                    2
                )
            else:
                pnl = round(
                    (entry_price - exit_price) * position_size
                        - total_commission,
                    2
                )

            if position_size == 0:
                return log, equity

            pnl_per = round(
                (((position_size * entry_price) + pnl)
                    / (position_size * entry_price) - 1) * 100,
                2
            )

            if log.shape[0] == 0:
                cum_pnl = round(pnl, 2)
                cum_pnl_per = round(
                    pnl / (initial_capital + pnl) * 100,
                    2
                )
            else:
                cum_pnl = round(pnl + log[-3], 2)
                cum_pnl_per = round(
                    pnl / (initial_capital + log[-3]) * 100,
                    2
                )

            log_row = np.array(
                [
                    deal_type, entry_signal, exit_signal, entry_date,
                    exit_date, entry_price, exit_price, position_size,
                    pnl, pnl_per, cum_pnl, cum_pnl_per, total_commission
                ]
            )
            log = np.concatenate((log, log_row))
            equity += pnl
            return log, equity

        for i in range(time.shape[0]):
            alert_open_long = False
            alert_close_long = False

            if i > 0:
                entry_price_2[i] = entry_price_2[i - 1]
                entry_price_3[i] = entry_price_3[i - 1]
                entry_price_4[i] = entry_price_4[i - 1]
                take_price[i] = take_price[i - 1]

            # Check of liquidation
            if (deal_type == 0 and low[i] <= liquidation_price):
                for deal in open_deals_log:
                    if not np.isnan(deal[0]):
                        completed_deals_log, equity = update_log(
                            completed_deals_log,
                            equity,
                            commission,
                            deal[0],
                            deal[1],
                            0,
                            deal[2],
                            time[i],
                            deal[3],
                            liquidation_price,
                            deal[4],
                            initial_capital
                        )

                open_deals_log = np.full((4, 5), np.nan)
                qty_entry = np.full(4, np.nan)
                deal_type = np.nan
                entry_signal = np.nan
                entry_date = np.nan
                entry_price = np.nan
                position_size = np.nan
                take_price[i] = np.nan
                entry_price_2[i] = np.nan
                entry_price_3[i] = np.nan
                entry_price_4[i] = np.nan
                alert_close_long = True

            # Trading logic (longs)
            if deal_type == 0:
                if close[i] <= open[i]:
                    if not np.isnan(take_price[i]) and high[i] >= take_price[i]:
                        for deal in open_deals_log:
                            if not np.isnan(deal[0]):
                                completed_deals_log, equity = update_log(
                                    completed_deals_log,
                                    equity,
                                    commission,
                                    deal[0],
                                    deal[1],
                                    13,
                                    deal[2],
                                    time[i],
                                    deal[3],
                                    close[i],
                                    deal[4],
                                    initial_capital
                                )

                        open_deals_log = np.full((4, 5), np.nan)
                        qty_entry = np.full(4, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[i] = np.nan
                        entry_price_2[i] = np.nan
                        entry_price_3[i] = np.nan
                        entry_price_4[i] = np.nan
                        alert_close_long = True

                if not np.isnan(entry_price_2[i]) and low[i] <= entry_price_2[i]:
                    entry_signal = 3
                    entry_price = entry_price_2[i]
                    entry_date = time[i]

                    open_deals_log[1] = np.array(
                        [
                            deal_type, entry_signal, entry_date,
                            entry_price, qty_entry[1]
                        ]
                    )

                    avg_entry_price = np.nansum(
                        open_deals_log[:2, 3] * open_deals_log[:2, 4]
                    ) / np.nansum(open_deals_log[:2, 4])
                    liquidation_price = adjust(
                        avg_entry_price * (1 - (1 / leverage)),
                        p_precision
                    )
                    take_price[i] = adjust(
                        avg_entry_price * (100 + take_profit) / 100,
                        p_precision
                    )

                    entry_price_2[i] = np.nan

                if not np.isnan(entry_price_3[i]) and low[i] <= entry_price_3[i]:
                    entry_signal = 4
                    entry_price = entry_price_3[i]
                    entry_date = time[i]

                    open_deals_log[2] = np.array(
                        [
                            deal_type, entry_signal, entry_date,
                            entry_price, qty_entry[2]
                        ]
                    )

                    avg_entry_price = np.nansum(
                        open_deals_log[:3, 3] * open_deals_log[:3, 4]
                    ) / np.nansum(open_deals_log[:3, 4])
                    liquidation_price = adjust(
                        avg_entry_price * (1 - (1 / leverage)),
                        p_precision
                    )
                    take_price[i] = adjust(
                        avg_entry_price * (100 + take_profit) / 100,
                        p_precision
                    )

                    entry_price_3[i] = np.nan

                if not np.isnan(entry_price_4[i]) and low[i] <= entry_price_4[i]:
                    entry_signal = 5
                    entry_price = entry_price_4[i]
                    entry_date = time[i]

                    open_deals_log[3] = np.array(
                        [
                            deal_type, entry_signal, entry_date,
                            entry_price, qty_entry[3]
                        ]
                    )

                    avg_entry_price = np.nansum(
                        open_deals_log[:, 3] * open_deals_log[:, 4]
                    ) / np.nansum(open_deals_log[:, 4])
                    liquidation_price = adjust(
                        avg_entry_price * (1 - (1 / leverage)),
                        p_precision
                    )
                    take_price[i] = adjust(
                        avg_entry_price * (100 + take_profit) / 100,
                        p_precision
                    )

                    entry_price_4[i] = np.nan

                if close[i] > open[i]:
                    if not np.isnan(take_price[i]) and high[i] >= take_price[i]:
                        for deal in open_deals_log:
                            if not np.isnan(deal[0]):
                                completed_deals_log, equity = update_log(
                                    completed_deals_log,
                                    equity,
                                    commission,
                                    deal[0],
                                    deal[1],
                                    13,
                                    deal[2],
                                    time[i],
                                    deal[3],
                                    close[i],
                                    deal[4],
                                    initial_capital
                                )

                        open_deals_log = np.full((4, 5), np.nan)
                        qty_entry = np.full(4, np.nan)
                        deal_type = np.nan
                        entry_signal = np.nan
                        entry_date = np.nan
                        entry_price = np.nan
                        position_size = np.nan
                        take_price[i] = np.nan
                        entry_price_2[i] = np.nan
                        entry_price_3[i] = np.nan
                        entry_price_4[i] = np.nan
                        alert_close_long = True

            entry_long = (
                high[i] - low[i] >= sma[i] * mult and
                low[i] < lowest[i] and
                close[i] >= high[i] - (high[i] - low[i]) 
                    * range_threshold / 100 and
                np.isnan(position_size)  
            )

            if entry_long:
                deal_type = 0
                entry_signal = 2
                entry_price = close[i]
                entry_date = time[i]

                if order_size_type == 0:
                    initial_position =  (
                        equity * leverage * (order_size / 100.0)
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                elif order_size_type == 1:
                    initial_position = (
                        order_size * leverage
                    )
                    position_size = (
                        initial_position * (1 - commission / 100)
                        / entry_price
                    )
                    
                liquidation_price = adjust(
                    entry_price * (1 - (1 / leverage)), p_precision
                )
                entry_price_2[i] = adjust(
                    close[i] * (100 - entry_percent_2) / 100, p_precision
                )
                entry_price_3[i] = adjust(
                    entry_price_2[i] * (100 - entry_percent_3) / 100,
                    p_precision
                )
                entry_price_4[i] = adjust(
                    entry_price_3[i] * (100 - entry_percent_4) / 100,
                    p_precision
                )
                take_price[i] = adjust(
                    close[i] * (100 + take_profit) / 100, p_precision
                )
                position_size = adjust(
                    position_size, q_precision
                )
                qty_entry[0] = adjust(
                    position_size * entry_volume[0] / 100, q_precision
                )
                qty_entry[1] = adjust(
                    position_size * entry_volume[1] / 100, q_precision
                )
                qty_entry[2] = adjust(
                    position_size * entry_volume[2] / 100, q_precision
                )
                qty_entry[3] = adjust(
                    position_size * entry_volume[3] / 100, q_precision
                )

                if np.any(qty_entry == 0):
                    break

                open_deals_log[0] = np.array(
                    [
                        deal_type, entry_signal, entry_date,
                        entry_price, qty_entry[0]
                    ]
                )
                alert_open_long = True

        return (
            completed_deals_log,
            open_deals_log,
            entry_price_2,
            entry_price_3,
            entry_price_4,
            take_price,
            alert_open_long,
            alert_close_long
        )
    
    def trade(self) -> None:
        if self.order_ids is None:
            self.order_ids = self.cache.load(self.symbol)

        if self.alert_close_long:
            self.client.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )
            self.client.cancel_all_orders(self.symbol)

        self.order_ids['limit_ids'] = self.client.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_open_long:
            self.client.cancel_all_orders(self.symbol)
            self.order_ids['limit_ids'] = self.client.check_limit_orders(
                symbol=self.symbol,
                order_ids=self.order_ids['limit_ids']
            )

            self.client.market_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size'] *
                       self.params['entry_volume'][0] / 100}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            order_id = self.client.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size'] *
                       self.params['entry_volume'][1] / 100}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_2[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size'] *
                       self.params['entry_volume'][2] / 100}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_3[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

            order_id = self.client.limit_open_long(
                symbol=self.symbol,
                size=(
                    f'{self.params['order_size'] *
                       self.params['entry_volume'][3] / 100}'
                    f'{'u' if self.params['order_size_type'] else '%'}'
                ),
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                price=self.entry_price_4[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)

        self.cache.save(self.symbol, self.order_ids)