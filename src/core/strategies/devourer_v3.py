import numpy as np
import numba as nb

from . import (
    BaseStrategy,
    BaseExchangeClient,
    adjust,
    colors,
    quantklines,
    update_completed_deals_log
)


class DevourerV3(BaseStrategy):
    # Strategy parameters
    params = {
        'position_size': 5.0,
        'stop_atr_p2': 0.5,
        'stop_atr_p3': 1.0,
        'take_atr_p3': 3.0,
        'fast_len_p1': 12,
        'slow_len_p1': 26,
        'sig_len_p1': 14,
        'k_len_p1': 14,
        'd_len_p1': 3,
        'kd_limit_p1': 70.0,
        'atr_len_p1': 10,
        'factor_p1': 2.0,
        'body_atr_coef_p1': 2.0,
        'ema_len_p1': 20,
        'atr_len_p2': 14,
        'highest_len_p2': 10,
        'correction_p2': 37.0,
        'ema_len_p2': 5,
        'atr_len_p3': 14,
        'ema_len_p3': 55,
        'close_under_ema_p3': 3
    }

    # Parameters to be optimized and their possible values
    opt_params = {
        'stop_atr_p2': [i / 10 for i in range(1, 30)],
        'stop_atr_p3': [i / 10 for i in range(1, 30)],
        'take_atr_p3': [i / 10 for i in range(10, 60)],
        'fast_len_p1': [i for i in range(6, 20)],
        'slow_len_p1': [i for i in range(20, 50)],
        'sig_len_p1': [i for i in range(8, 25)],
        'k_len_p1': [i for i in range(10, 20)],
        'd_len_p1': [i for i in range(2, 6)],
        'kd_limit_p1': [float(i) for i in range(40, 100, 5)],
        'atr_len_p1': [i for i in range(5, 20)],
        'factor_p1': [i / 10 for i in range(10, 40)],
        'body_atr_coef_p1': [i / 10 for i in range(5, 30)],
        'ema_len_p1': [i for i in range(5, 30)],
        'atr_len_p2': [i for i in range(5, 30)],
        'highest_len_p2': [i for i in range(5, 20)],
        'correction_p2': [float(i) for i in range(20, 50)],
        'ema_len_p2': [i for i in range(2, 15)],
        'atr_len_p3': [i for i in range(5, 25)],
        'ema_len_p3': [i for i in range(40, 80)],
        'close_under_ema_p3': [i for i in range(1, 5)]
    }

    # Frontend rendering settings for indicators
    indicator_options = {
        'SL': {
            'pane': 0,
            'type': 'line',
            'color': colors.CRIMSON
        },
        'TP': {
            'pane': 0,
            'type': 'line',
            'color': colors.GREEN
        }
    }

    def __init__(self, params: dict | None = None) -> None:
        super().__init__(params)

    def calculate(self, market_data) -> None:
        super().init_variables(market_data)

        self.stop_price = np.full(self.time.shape[0], np.nan)
        self.take_price = np.full(self.time.shape[0], np.nan)
        self.liquidation_price = np.nan

        self.deal_p1 = False
        self.deal_p2 = False
        self.deal_p3 = False

        self.filter1_p1 = False
        self.filter2_p1 = False
        self.filter3_p1 = False
        self.short_allowed_p3 = False

        self.close_under_ema_counter_p3 = 0

        self.macd_p1 = (
            quantklines.ema(
                source=self.close,
                length=self.params['fast_len_p1']
            ) -
            quantklines.ema(
                source=self.close,
                length=self.params['slow_len_p1']
            )
        )
        self.signal_p1 = quantklines.ema(
            source=self.macd_p1,
            length=self.params['sig_len_p1']
        )
        self.k_p1 = quantklines.stoch(
            source=self.close,
            high=self.high,
            low=self.low,
            length=self.params['k_len_p1']
        )
        self.d_p1 = quantklines.sma(source=self.k_p1, length=self.params['d_len_p1'])
        supertrend = quantklines.supertrend(
            high=self.high,
            low=self.low,
            close=self.close,
            factor=self.params['factor_p1'],
            atr_length=self.params['atr_len_p1']
        )
        self.direction_p1 = supertrend[1]
        self.atr_p1 = quantklines.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p1']
        )
        self.ema_p1 = quantklines.ema(
            source=quantklines.highest(
                source=self.close,
                length=self.params['ema_len_p1']
            ),
            length=self.params['ema_len_p1']
        )
        self.cross_up1_p1 = quantklines.crossover(
            source1=self.macd_p1,
            source2=self.signal_p1
        )
        self.cross_down_p1 = quantklines.crossunder(
            source1=self.macd_p1,
            source2=self.signal_p1
        )
        self.cross_up2_p1 = quantklines.crossover(
            source1=self.close,
            source2=self.ema_p1
        )
        self.lower_band_p2 = (
            quantklines.highest(
                source=self.high,
                length=self.params['highest_len_p2']
            ) * (self.params['correction_p2'] - 100) / -100
        )
        self.signal_p2 = quantklines.ema(
            source=self.macd_p1,
            length=self.params['ema_len_p2']
        )
        self.cross_p2 = quantklines.cross(source1=self.signal_p2, source2=self.macd_p1)
        self.atr_p2 = quantklines.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p2']
        )
        self.ema_p3 = quantklines.ema(
            source=quantklines.ema(
                source=quantklines.ema(
                    source=self.close,
                    length=self.params['ema_len_p3']
                ),
                length=self.params['ema_len_p3']
            ),
            length=self.params['ema_len_p3']
        )
        self.atr_p3 = quantklines.atr(
            high=self.high,
            low=self.low,
            close=self.close,
            length=self.params['atr_len_p3']
        )

        self.alert_cancel = False
        self.alert_open_long = False
        self.alert_close_long = False
        self.alert_open_short = False
        self.alert_close_short = False

        (
            self.completed_deals_log,
            self.open_deals_log,
            self.take_price,
            self.stop_price,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_close_long,
            self.alert_open_short,
            self.alert_close_short
        ) = self._calculate_loop(
            self.params['direction'],
            self.params['initial_capital'],
            self.params['commission'],
            self.params['position_size_type'],
            self.params['position_size'],
            self.params['leverage'],
            self.params['stop_atr_p2'],
            self.params['stop_atr_p3'],
            self.params['take_atr_p3'],
            self.params['kd_limit_p1'],
            self.params['body_atr_coef_p1'],
            self.params['close_under_ema_p3'],
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
            self.position_type,
            self.order_signal,
            self.order_date,
            self.order_price,
            self.take_price,
            self.stop_price,
            self.liquidation_price,
            self.order_size,
            self.deal_p1,
            self.deal_p2,
            self.deal_p3,
            self.filter1_p1,
            self.filter2_p1,
            self.filter3_p1,
            self.short_allowed_p3,
            self.close_under_ema_counter_p3,
            self.macd_p1,
            self.signal_p1,
            self.k_p1,
            self.d_p1,
            self.direction_p1,
            self.atr_p1,
            self.cross_up1_p1,
            self.cross_down_p1,
            self.cross_up2_p1,
            self.lower_band_p2,
            self.cross_p2,
            self.atr_p2,
            self.ema_p3,
            self.atr_p3,
            self.alert_cancel,
            self.alert_open_long,
            self.alert_close_long,
            self.alert_open_short,
            self.alert_close_short
        )

        self.indicators = {
            'SL': {
                'options': self.indicator_options['SL'],
                'values': self.stop_price
            },
            'TP': {
                'options': self.indicator_options['TP'],
                'values': self.take_price
            }
        }

    @staticmethod
    @nb.njit(cache=True, nogil=True)
    def _calculate_loop(
        direction: int,
        initial_capital: float,
        commission: float,
        position_size_type: int,
        position_size: float,
        leverage: int,
        stop_atr_p2: float,
        stop_atr_p3: float,
        take_atr_p3: float,
        kd_limit_p1: float,
        body_atr_coef_p1: float,
        close_under_ema_p3,
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
        position_type: float,
        order_signal: float,
        order_date: float,
        order_price: float,
        take_price: np.ndarray,
        stop_price: np.ndarray,
        liquidation_price: float,
        order_size: float,
        deal_p1: bool,
        deal_p2: bool,
        deal_p3: bool,
        filter1_p1: bool,
        filter2_p1: bool,
        filter3_p1: bool,
        short_allowed_p3: bool,
        close_under_ema_counter_p3: int,
        macd_p1: np.ndarray,
        signal_p1: np.ndarray,
        k_p1: np.ndarray,
        d_p1: np.ndarray,
        direction_p1: np.ndarray,
        atr_p1: np.ndarray,
        cross_up1_p1: np.ndarray,
        cross_down_p1: np.ndarray,
        cross_up2_p1: np.ndarray,
        lower_band_p2: np.ndarray,
        cross_p2: np.ndarray,
        atr_p2: np.ndarray,
        ema_p3: np.ndarray,
        atr_p3: np.ndarray,
        alert_cancel: bool,
        alert_open_long: bool,
        alert_close_long: bool,
        alert_open_short: bool,
        alert_close_short: bool
    ) -> tuple:
        for i in range(2, time.shape[0]):
            stop_price[i] = stop_price[i - 1]
            take_price[i] = take_price[i - 1]

            alert_cancel = False
            alert_open_long = False
            alert_close_long = False
            alert_open_short = False
            alert_close_short = False

            # Pattern #3 — indicators
            if close[i] > ema_p3[i]:
                short_allowed_p3 = True

            if close[i] < ema_p3[i]:
                close_under_ema_counter_p3 += 1
            else:
                close_under_ema_counter_p3 = 0

            # Pattern #1 — filters
            filter1_p1_off = (
                filter1_p1 and (
                    direction_p1[i] < 0 and (
                        direction_p1[i - 1] > 0 and (
                            k_p1[i] < kd_limit_p1 or 
                            d_p1[i] < kd_limit_p1
                        )
                    ) or 
                    macd_p1[i] < signal_p1[i]
                )
            )
            filter1_p1_on = direction_p1[i] > 0 and close[i] < ema_p3[i]

            if filter1_p1_off:
                filter1_p1 = False
            elif filter1_p1_on:
                filter1_p1 = True

            filter2_p1_off = filter2_p1 and cross_down_p1[i]
            filter2_p1_on = (
                close[i] < ema_p3[i] and
                close[i] > open[i] and
                (close[i] - open[i]) / atr_p1[i - 1] > body_atr_coef_p1
            )

            if filter2_p1_off:
                filter2_p1 = False
            elif filter2_p1_on:
                filter2_p1 = True

            filter3_p1_off = filter3_p1
            filter3_p1_on = (
                macd_p1[i - 1] < signal_p1[i - 1] and
                macd_p1[i - 2] > signal_p1[i - 2]
            )

            if filter3_p1_off:
                filter3_p1 = False
            elif filter3_p1_on:
                filter3_p1 = True

            # Check of liquidation
            if (deal_p1 or deal_p1) and low[i] <= liquidation_price:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    700,
                    order_date,
                    time[i],
                    order_price,
                    liquidation_price,
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                deal_p1 = False
                deal_p2 = False

            if deal_p3 and high[i] >= liquidation_price:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    800,
                    order_date,
                    time[i],
                    order_price,
                    liquidation_price,
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                deal_p3 = False
                alert_cancel = True

            # Pattern #1
            exit_long_p1 = (
                cross_down_p1[i] and
                deal_p1
            )
            entry_long1_p1 = (
                macd_p1[i] > signal_p1[i] and
                low[i] > lower_band_p2[i] and
                not filter1_p1
            )
            entry_long2_p1 = (
                macd_p1[i] > signal_p1[i] and
                low[i] > lower_band_p2[i] and
                cross_up2_p1[i] and
                filter1_p1
            )
            entry_long_p1 = (
                (entry_long1_p1 or entry_long2_p1) and
                not filter2_p1 and
                not filter3_p1 and
                not deal_p1 and
                not deal_p2 and
                (direction == 0 or direction == 1)
            )

            if exit_long_p1:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    100,
                    order_date,
                    time[i],
                    order_price,
                    close[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                deal_p1 = False
                alert_close_long = True
            elif entry_long_p1:
                deal_p1 = True

                if deal_p3:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        200,
                        order_date,
                        time[i],
                        order_price,
                        close[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    liquidation_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    deal_p3 = False
                    short_allowed_p3 = False
                    alert_close_short = True
                    alert_cancel = True

                if deal_p2:
                    deal_p2 = False
                    stop_price[i] = np.nan
                else:
                    position_type = 0
                    order_signal = 100
                    order_price = close[i]

                    if position_size_type == 0:
                        initial_position =  (
                            equity * leverage * (position_size / 100.0)
                        )
                        order_size = (
                            initial_position * (1 - commission / 100)
                            / order_price
                        )
                    elif position_size_type == 1:
                        initial_position = (
                            position_size * leverage
                        )
                        order_size = (
                            initial_position * (1 - commission / 100)
                            / order_price
                        )
                        
                    order_date = time[i]
                    liquidation_price = adjust(
                        order_price * (1 - (1 / leverage)), p_precision
                    )
                    order_size = adjust(
                        order_size, q_precision
                    )
                    open_deals_log[0] = np.array(
                        [
                            position_type, order_signal, order_date,
                            order_price, order_size
                        ]
                    )
                    alert_open_long = True

            # Pattern #2
            exit_long_p2 = (
                (cross_p2[i] or close[i] < stop_price[i]) and
                deal_p2
            )
            entry_long_p2 = (
                low[i] <= lower_band_p2[i] and
                not deal_p2 and
                (direction == 0 or direction == 1)
            )

            if exit_long_p2:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    100,
                    order_date,
                    time[i],
                    order_price,
                    close[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                deal_p2 = False
                alert_close_long = True
            elif entry_long_p2:
                deal_p2 = True

                if deal_p1:
                    deal_p1 = False

                if deal_p3:
                    completed_deals_log, pnl = update_completed_deals_log(
                        completed_deals_log,
                        commission,
                        position_type,
                        order_signal,
                        200,
                        order_date,
                        time[i],
                        order_price,
                        close[i],
                        order_size,
                        initial_capital
                    )
                    equity += pnl

                    open_deals_log[:] = np.nan
                    position_type = np.nan
                    order_signal = np.nan
                    order_date = np.nan
                    order_price = np.nan
                    liquidation_price = np.nan
                    take_price[i] = np.nan
                    stop_price[i] = np.nan
                    order_size = np.nan
                    deal_p3 = False
                    short_allowed_p3 = False
                    alert_close_short = True
                    alert_cancel = True

                position_type = 0
                order_signal = 100
                order_price = close[i]

                if position_size_type == 0:
                    initial_position =  (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                elif position_size_type == 1:
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                    
                order_date = time[i]
                stop_price[i] = adjust(
                    close[i] - atr_p2[i] * stop_atr_p2, p_precision
                )
                liquidation_price = adjust(
                    order_price * (1 - (1 / leverage)), p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )
                alert_open_long = True

            # Pattern #3
            if deal_p3 and low[i] <= take_price[i]:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    400,
                    order_date,
                    time[i],
                    order_price,
                    take_price[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                liquidation_price = np.nan
                order_size = np.nan
                deal_p3 = False
                short_allowed_p3 = False

            exit_short_p3 = (
                (
                    (close[i] > stop_price[i] or cross_up1_p1[i]) and deal_p3
                ) or 
                (low[i] < lower_band_p2[i] and deal_p3)
            )
            entry_short_p3 = (
                short_allowed_p3 and
                close_under_ema_counter_p3 >= close_under_ema_p3 and
                macd_p1[i] < signal_p1[i] and
                not deal_p1 and
                not deal_p2 and
                not deal_p3 and
                (direction == 0 or direction == 2)
            )

            if exit_short_p3:
                completed_deals_log, pnl = update_completed_deals_log(
                    completed_deals_log,
                    commission,
                    position_type,
                    order_signal,
                    200,
                    order_date,
                    time[i],
                    order_price,
                    close[i],
                    order_size,
                    initial_capital
                )
                equity += pnl

                open_deals_log[:] = np.nan
                position_type = np.nan
                order_signal = np.nan
                order_date = np.nan
                order_price = np.nan
                liquidation_price = np.nan
                take_price[i] = np.nan
                stop_price[i] = np.nan
                order_size = np.nan
                deal_p3 = False
                short_allowed_p3 = False
                alert_close_short = True
                alert_cancel = True
            elif entry_short_p3:
                deal_p3 = True
                position_type = 1
                order_signal = 200
                order_price = close[i]

                if position_size_type == 0:
                    initial_position = (
                        equity * leverage * (position_size / 100.0)
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )
                elif position_size_type == 1:
                    initial_position = (
                        position_size * leverage
                    )
                    order_size = (
                        initial_position * (1 - commission / 100)
                        / order_price
                    )

                order_date = time[i]
                stop_price[i] = adjust(
                    close[i] + atr_p3[i] * stop_atr_p3, p_precision
                )
                take_price[i] = adjust(
                    close[i] - atr_p3[i] * take_atr_p3, p_precision
                )
                liquidation_price = adjust(
                    order_price * (1 + (1 / leverage)), p_precision
                )
                order_size = adjust(
                    order_size, q_precision
                )
                open_deals_log[0] = np.array(
                    [
                        position_type, order_signal, order_date,
                        order_price, order_size
                    ]
                )
                alert_open_short = True

        return (
            completed_deals_log,
            open_deals_log,
            take_price,
            stop_price,
            alert_cancel,
            alert_open_long,
            alert_close_long,
            alert_open_short,
            alert_close_short
        )

    def _trade(self, client: BaseExchangeClient) -> None:
        if self.alert_cancel:
            client.trade.cancel_all_orders(self.symbol)

        self.order_ids['stop_ids'] = client.trade.check_stop_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['stop_ids']
        )
        self.order_ids['limit_ids'] = client.trade.check_limit_orders(
            symbol=self.symbol,
            order_ids=self.order_ids['limit_ids']
        )

        if self.alert_close_long:
            client.trade.market_close_long(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_close_short:
            client.trade.market_close_short(
                symbol=self.symbol,
                size='100%',
                hedge=False
            )

        if self.alert_open_long:
            client.trade.market_open_long(
                symbol=self.symbol,
                size=f'{self.params['position_size']}%',
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            if not np.isnan(self.stop_price[-1]):
                order_id = client.trade.market_stop_close_long(
                    symbol=self.symbol, 
                    size='100%', 
                    price=self.stop_price[-1], 
                    hedge=False
                )

                if order_id:
                    self.order_ids['stop_ids'].append(order_id)

        if self.alert_open_short:
            client.trade.market_open_short(
                symbol=self.symbol,
                size=f'{self.params['position_size']}%',
                margin=(
                    'cross' if self.params['margin_type'] else 'isolated'
                ),
                leverage=self.params['leverage'],
                hedge=False
            )

            order_id = client.trade.market_stop_close_short(
                symbol=self.symbol, 
                size='100%',
                price=self.stop_price[-1], 
                hedge=False
            )

            if order_id:
                self.order_ids['stop_ids'].append(order_id)

            order_id = client.trade.limit_close_short(
                symbol=self.symbol,
                size='100%',
                price=self.take_price[-1],
                hedge=False
            )

            if order_id:
                self.order_ids['limit_ids'].append(order_id)