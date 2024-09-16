import warnings
import ast
import os

import numpy as np

from src.flask_app import FlaskApp
from src import BinanceClient
from src import BybitClient
from src import Strategies
from src import DealKeywords
from src import Preprocessor


class Tester():
    def __init__(self, testing):
        self.strategies = dict()

        for strategy in Strategies.registry.values():
            folder_path = os.path.abspath(
                f'src/strategies/{strategy[0]}/backtesting/'
            )
            file_names = os.listdir(folder_path)

            for name in file_names.copy():
                if not name.endswith('.txt'):
                    file_names.remove(name)

            for name in file_names:
                exchange = name[:name.find('_')]
                symbol = name[
                    name.find('_', name.find('_')) + 1 : name.rfind('_')
                ]
                interval = name[
                    name.rfind('_') + 1 : name.rfind('.')
                ]

                if exchange.lower() == 'binance':
                    client = BinanceClient()
                elif exchange.lower() == 'bybit':
                    client = BybitClient()

                file_path = os.path.abspath(
                    f'src/strategies/{strategy[0]}/backtesting/{name}'
                )
                target_line = False
                opt_parameters = []
                parameters = []

                with open(file_path, 'r') as file:
                    for line_num, line in enumerate(file):
                        if line_num == 0:
                            start = line[:line.find(' - ')].lstrip('Period: ')
                            end = line[
                                line.find(' - ') + 3 : line.find('\n')
                            ]

                        if target_line and line.startswith('='):
                            opt_parameters.append(parameters.copy())
                            parameters.clear()
                            target_line = False
                            continue

                        if target_line:
                            parameters.append(
                                ast.literal_eval(
                                    line[line.find('= ') + 2 :]
                                )
                            )

                        if line.startswith('='):
                            target_line = True

                for parameters in opt_parameters:
                    client.get_data(symbol, interval, start, end)
                    strategy_obj = strategy[1](
                        client, opt_parameters=parameters
                    )
                    all_parameters = strategy_obj.__dict__.copy()
                    all_parameters.pop('client')
                    strategy_data = {
                        'name': strategy[0],
                        'exchange': exchange.lower(),
                        'symbol': symbol,
                        'interval': interval,
                        'mintick': client.price_precision,
                        'strategy': strategy_obj,
                        'parameters': all_parameters
                    }
                    self.strategies[str(id(strategy_data))] = strategy_data

        if len(self.strategies) == 0:
            exchange = testing['exchange']
            symbol = testing['symbol']
            interval = testing['interval']
            start = testing['date/time #1']
            end = testing['date/time #2']

            if exchange == 'binance':
                client =  BinanceClient()
            elif exchange == 'bybit':
                client = BybitClient()

            client.get_data(symbol, interval, start, end)
            strategy_obj = Strategies.registry[
                testing['strategy']
            ][1](client)
            all_parameters = strategy_obj.__dict__.copy()
            all_parameters.pop('client')
            strategy_data = {
                'name': Strategies.registry[testing['strategy']][0],
                'exchange': exchange.lower(),
                'symbol': symbol,
                'interval': interval,
                'mintick': client.price_precision,
                'strategy': strategy_obj,
                'parameters': all_parameters
            }
            self.strategies[str(id(strategy_data))] = strategy_data

        self.frontend_main_data = {}
        self.frontend_lite_data = {}

        for key, data in self.strategies.items():
            frontend_data = self.get_frontend_data(data)
            self.frontend_main_data[key] = frontend_data[0]
            self.frontend_lite_data[key] = frontend_data[1]

    def update_strategy(self, strategy, name, new_value):
        try:
            old_value = self.strategies[strategy]['parameters'][name]

            if isinstance(new_value, list):
                new_value = list(map(lambda x: float(x), new_value))
            else:
                new_value = ast.literal_eval(new_value.capitalize())

                if isinstance(old_value, float) and isinstance(new_value, int):
                    new_value = float(new_value)

            if type(old_value) != type(new_value):
                raise

            self.strategies[strategy]['parameters'][name] = new_value
            strategy_obj = self.strategies[strategy]['strategy'].__class__(
                self.strategies[strategy]['strategy'].client,
                all_parameters=list(
                    self.strategies[strategy]['parameters'].values()
                )
            )
            self.strategies[strategy]['strategy'] = strategy_obj
            frontend_data = self.get_frontend_data(self.strategies[strategy])
            self.frontend_main_data[strategy] = frontend_data[0]
            self.frontend_lite_data[strategy] = frontend_data[1]
        except Exception:
            raise

    def get_frontend_data(self, data):
        result = []
        strategy_obj = data['strategy']
        strategy_obj.start()
        completed_deals_log = data['strategy'] \
            .completed_deals_log.reshape((-1, 13))
        open_deals_log = data['strategy'].open_deals_log

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)

            equity = np.concatenate(
                (np.array([data['strategy'].initial_capital]),
                completed_deals_log[:, 8])
            ).cumsum()
            metrics = self.calculate(
                completed_deals_log, data['strategy'].initial_capital
            )

        result.append({
            'chartData': {
                'name': data['name'].capitalize().replace('_', '-'),
                'exchange': data['exchange'],
                'symbol': data['symbol'],
                'interval': data['interval'],
                'mintick': data['mintick'],
                'klines': Preprocessor.get_klines(
                    data['strategy'].client.price_data
                ),
                'indicators': Preprocessor.get_indicators(
                    data['strategy'].client.price_data,
                    data['strategy'].indicators
                ),
                'markers': Preprocessor.get_deals(
                    completed_deals_log,
                    open_deals_log,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                    data['strategy'].qty_precision
                ),
            },
            'reportData': {
                'equity': Preprocessor.get_equity(equity),
                'metrics': metrics,
                'completedDealsLog': Preprocessor.get_completed_deals_log(
                    completed_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals,
                    DealKeywords.exit_signals,
                ),
                'openDealsLog': Preprocessor.get_open_deals_log(
                    open_deals_log,
                    DealKeywords.deal_types,
                    DealKeywords.entry_signals
                )
            }
        })
        result.append({
            'name': data['name'].capitalize().replace('_', '-'),
            'exchange': data['exchange'],
            'symbol': data['symbol'],
            'interval': data['interval'],
            'mintick': data['mintick'],
            'parameters': data['parameters']
        })
        return result

    @staticmethod
    def calculate(log, initial_capital):
        # Gross profit
        all_gross_profit = round(log[:, 8][log[:, 8] > 0].sum(), 2)
        all_gross_profit_per = round(
            all_gross_profit / initial_capital * 100, 2
        )

        long_gross_profit = round(
            log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 0)].sum(), 2
        )
        long_gross_profit_per = round(
            long_gross_profit / initial_capital * 100, 2
        )

        short_gross_profit = round(
            log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 1)].sum(), 2
        )
        short_gross_profit_per = round(
            short_gross_profit / initial_capital * 100, 2
        )

        # Gross loss
        all_gross_loss = round(abs(log[:, 8][log[:, 8] <= 0].sum()), 2)
        all_gross_loss_per = round(
            all_gross_loss / initial_capital * 100, 2
        )

        long_gross_loss = round(
            abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 0)].sum()), 2
        )
        long_gross_loss_per = round(
            long_gross_loss / initial_capital * 100, 2
        )

        short_gross_loss = round(
            abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 1)].sum()), 2
        )
        short_gross_loss_per = round(
            short_gross_loss / initial_capital * 100, 2
        )

        # Net profit
        all_net_profit = round(all_gross_profit - all_gross_loss, 2)
        all_net_profit_per = round(
            all_net_profit / initial_capital * 100, 2
        )

        long_net_profit = round(long_gross_profit - long_gross_loss, 2)
        long_net_profit_per = round(
            long_net_profit / initial_capital * 100, 2
        )

        short_net_profit = round(short_gross_profit - short_gross_loss, 2)
        short_net_profit_per = round(
            short_net_profit / initial_capital * 100, 2
        )

        # Profit factor
        if all_gross_loss != 0:
            all_profit_factor = round(
                all_gross_profit / all_gross_loss, 3
            )
        else:
            all_profit_factor = np.nan

        if long_gross_loss != 0:
            long_profit_factor =  round(
                long_gross_profit / long_gross_loss, 3
            )
        else:
            long_profit_factor = np.nan

        if short_gross_loss != 0:
            short_profit_factor = round(
                short_gross_profit / short_gross_loss, 3
            )
        else:
            short_profit_factor = np.nan

        # Commission paid
        all_commission_paid = round(log[:, 12].sum(), 2)
        long_commission_paid = round(log[:, 12][log[:, 0] == 0].sum(), 2)
        short_commission_paid = round(log[:, 12][log[:, 0] == 1].sum(), 2)

        # Total closed trades
        all_total_closed_trades = log.shape[0]
        long_total_closed_trades = log[log[:, 0] == 0].shape[0]
        short_total_closed_trades = log[log[:, 0] == 1].shape[0]

        # Number winning trades
        all_number_winning_trades = log[log[:, 8] > 0].shape[0]
        long_number_winning_trades = log[
            (log[:, 8] > 0) & (log[:, 0] == 0)
        ].shape[0]
        short_number_winning_trades = log[
            (log[:, 8] > 0) & (log[:, 0] == 1)
        ].shape[0]

        # Number losing trades
        all_number_losing_trades = log[log[:, 8] <= 0].shape[0]
        long_number_losing_trades = log[
            (log[:, 8] <= 0) & (log[:, 0] == 0)
        ].shape[0]
        short_number_losing_trades = log[
            (log[:, 8] <= 0) & (log[:, 0] == 1)
        ].shape[0]

        # Percent profitable
        try:
            all_percent_profitable = round(
                all_number_winning_trades / 
                    all_total_closed_trades * 100,
                2
            )
        except Exception:
            all_percent_profitable = np.nan

        try:
            long_percent_profitable = round(
                long_number_winning_trades / 
                    long_total_closed_trades * 100,
                2
            )
        except Exception:
            long_percent_profitable = np.nan

        try:
            short_percent_profitable = round(
                short_number_winning_trades / 
                    short_total_closed_trades * 100,
                2
            )
        except Exception:
            short_percent_profitable = np.nan

        # Avg trade
        all_avg_trade = round(log[:, 8].mean(), 2)
        all_avg_trade_per = round(log[:, 9].mean(), 2)

        long_avg_trade = round(log[:, 8][log[:, 0] == 0].mean(), 2)
        long_avg_trade_per = round(log[:, 9][log[:, 0] == 0].mean(), 2)

        short_avg_trade = round(log[:, 8][log[:, 0] == 1].mean(), 2)
        short_avg_trade_per = round(log[:, 9][log[:, 0] == 1].mean(), 2)

        # Avg winning trade
        all_avg_winning_trade = round(log[:, 8][log[:, 8] > 0].mean(), 2)
        all_avg_winning_trade_per = round(
            log[:, 9][log[:, 9] > 0].mean(), 2
        )

        long_avg_winning_trade = round(
            log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 0)].mean(), 2
        )
        long_avg_winning_trade_per = round(
            log[:, 9][(log[:, 9] > 0) & (log[:, 0] == 0)].mean(), 2
        )

        short_avg_winning_trade = round(
            log[:, 8][(log[:, 8] > 0) & (log[:, 0] == 1)].mean(), 2
        )
        short_avg_winning_trade_per = round(
            log[:, 9][(log[:, 9] > 0) & (log[:, 0] == 1)].mean(), 2
        )

        # Avg losing trade
        all_avg_losing_trade = round(
            abs(log[:, 8][log[:, 8] <= 0].mean()), 2
        )
        all_avg_losing_trade_per = round(
            abs(log[:, 9][log[:, 9] <= 0].mean()), 2
        )

        long_avg_losing_trade = round(
            abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 0)].mean()), 2
        )
        long_avg_losing_trade_per = round(
            abs(log[:, 9][(log[:, 9] <= 0) & (log[:, 0] == 0)].mean()), 2
        )

        short_avg_losing_trade = round(
            abs(log[:, 8][(log[:, 8] <= 0) & (log[:, 0] == 1)].mean()), 2
        )
        short_avg_losing_trade_per = round(
            abs(log[:, 9][(log[:, 9] <= 0) & (log[:, 0] == 1)].mean()), 2
        )

        # Ratio avg win / avg loss
        all_ratio_avg_win_loss = round(
            all_avg_winning_trade / all_avg_losing_trade, 3
        )
        long_ratio_avg_win_loss = round(
            long_avg_winning_trade / long_avg_losing_trade, 3
        )
        short_ratio_avg_win_loss = round(
            short_avg_winning_trade / short_avg_losing_trade, 3
        )

        # Largest winning trade
        all_largest_winning_trade = np.nan
        all_largest_winning_trade_per = np.nan

        try:
            all_largest_winning_trade = round(log[:, 8].max(), 2)
            all_largest_winning_trade_per = round(log[:, 9].max(), 2)
        except Exception:
            pass

        long_largest_winning_trade = np.nan
        long_largest_winning_trade_per = np.nan

        try:
            long_largest_winning_trade = round(
                log[:, 8][log[:, 0] == 0].max(), 2
            )
            long_largest_winning_trade_per = round(
                log[:, 9][log[:, 0] == 0].max(), 2
            )
        except Exception:
            pass

        short_largest_winning_trade = np.nan
        short_largest_winning_trade_per = np.nan

        try:
            short_largest_winning_trade = round(
                log[:, 8][log[:, 0] == 1].max(), 2
            )
            short_largest_winning_trade_per = round(
                log[:, 9][log[:, 0] == 1].max(), 2
            )
        except Exception:
            pass

        # Largest losing trade
        all_largest_losing_trade = np.nan
        all_largest_losing_trade_per = np.nan

        try:
            all_largest_losing_trade = round(abs(log[:, 8].min()), 2)
            all_largest_losing_trade_per = round(abs(log[:, 9].min()), 2)
        except Exception:
            pass

        long_largest_losing_trade = np.nan
        long_largest_losing_trade_per = np.nan  

        try:
            long_largest_losing_trade = round(
                abs(log[:, 8][log[:, 0] == 0].min()), 2
            )
            long_largest_losing_trade_per = round(
               abs(log[:, 9][log[:, 0] == 0].min()), 2
            )
        except Exception:
            pass

        short_largest_losing_trade = np.nan
        short_largest_losing_trade_per = np.nan

        try:
            short_largest_losing_trade = round(
                abs(log[:, 8][log[:, 0] == 1].min()), 2
            )
            short_largest_losing_trade_per = round(
                abs(log[:, 9][log[:, 0] == 1].min()), 2
            )
        except Exception:
            pass

        # Max drawdown
        try:
            equity = np.concatenate(
                (np.array([initial_capital]), log[:, 8])
            ).cumsum()
            max_equity = equity[0]
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

            for i in range(1, equity.shape[0]):
                if equity[i] > max_equity:
                    max_equity = equity[i]

                if equity[i] < equity[i - 1]:
                    min_equity = equity[i]
                    drawdown = max_equity - min_equity
                    drawdown_per = -(min_equity / max_equity - 1) * 100

                    if drawdown > all_max_drawdown:
                        all_max_drawdown = round(drawdown, 2)

                    if drawdown_per > all_max_drawdown_per:
                        all_max_drawdown_per = round(drawdown_per, 2)
        except Exception:
            all_max_drawdown = 0.0
            all_max_drawdown_per = 0.0

        # Sortino ratio
        all_sortino_ratio = round(
            all_avg_trade_per / 
                (log[:, 9][log[:, 9] <= 0] ** 2).mean() ** 0.5,
            3
        )

        metrics = [
            [
                all_net_profit,
                all_net_profit_per,
                all_gross_profit,
                all_gross_profit_per,
                all_gross_loss,
                all_gross_loss_per,
                "" if np.isnan(all_profit_factor)
                    else all_profit_factor,
                all_commission_paid,
                all_total_closed_trades,
                all_number_winning_trades,
                all_number_losing_trades,
                "" if np.isnan(all_percent_profitable)
                    else all_percent_profitable,
                "" if np.isnan(all_avg_trade)
                    else all_avg_trade,
                "" if np.isnan(all_avg_trade_per)
                    else all_avg_trade_per,
                "" if np.isnan(all_avg_winning_trade)
                    else all_avg_winning_trade,
                "" if np.isnan(all_avg_winning_trade_per)
                    else all_avg_winning_trade_per,
                "" if np.isnan(all_avg_losing_trade)
                    else all_avg_losing_trade,
                "" if np.isnan(all_avg_losing_trade_per)
                    else all_avg_losing_trade_per,
                "" if np.isnan(all_ratio_avg_win_loss)
                    else all_ratio_avg_win_loss,
                "" if np.isnan(all_largest_winning_trade)
                    else all_largest_winning_trade,
                "" if np.isnan(all_largest_winning_trade_per)
                    else all_largest_winning_trade_per,
                "" if np.isnan(all_largest_losing_trade)
                    else all_largest_losing_trade,
                "" if np.isnan(all_largest_losing_trade_per)
                    else all_largest_losing_trade_per,
                "" if np.isnan(all_max_drawdown)
                    else all_max_drawdown,
                "" if np.isnan(all_max_drawdown_per)
                    else all_max_drawdown_per,
                "" if np.isnan(all_sortino_ratio)
                    else all_sortino_ratio
            ],
            [
                long_net_profit,
                long_net_profit_per,
                long_gross_profit,
                long_gross_profit_per,
                long_gross_loss,
                long_gross_loss_per,
                "" if np.isnan(long_profit_factor)
                    else long_profit_factor,
                long_commission_paid,
                long_total_closed_trades,
                long_number_winning_trades,
                long_number_losing_trades,
                "" if np.isnan(long_percent_profitable)
                    else long_percent_profitable,
                "" if np.isnan(long_avg_trade)
                    else long_avg_trade,
                "" if np.isnan(long_avg_trade_per)
                    else long_avg_trade_per,
                "" if np.isnan(long_avg_winning_trade)
                    else long_avg_winning_trade,
                "" if np.isnan(long_avg_winning_trade_per)
                    else long_avg_winning_trade_per,
                "" if np.isnan(long_avg_losing_trade)
                    else long_avg_losing_trade,
                "" if np.isnan(long_avg_losing_trade_per)
                    else long_avg_losing_trade_per,
                "" if np.isnan(long_ratio_avg_win_loss)
                    else long_ratio_avg_win_loss,
                "" if np.isnan(long_largest_winning_trade)
                    else long_largest_winning_trade,
                "" if np.isnan(long_largest_winning_trade_per)
                    else long_largest_winning_trade_per,
                "" if np.isnan(long_largest_losing_trade)
                    else long_largest_losing_trade,
                "" if np.isnan(long_largest_losing_trade_per)
                    else long_largest_losing_trade_per
            ],
            [
                short_net_profit,
                short_net_profit_per,
                short_gross_profit,
                short_gross_profit_per,
                short_gross_loss,
                short_gross_loss_per,
                "" if np.isnan(short_profit_factor)
                    else short_profit_factor,
                short_commission_paid,
                short_total_closed_trades,
                short_number_winning_trades,
                short_number_losing_trades,
                "" if np.isnan(short_percent_profitable)
                    else short_percent_profitable,
                "" if np.isnan(short_avg_trade)
                    else short_avg_trade,
                "" if np.isnan(short_avg_trade_per)
                    else short_avg_trade_per,
                "" if np.isnan(short_avg_winning_trade)
                    else short_avg_winning_trade,
                "" if np.isnan(short_avg_winning_trade_per)
                    else short_avg_winning_trade_per,
                "" if np.isnan(short_avg_losing_trade)
                    else short_avg_losing_trade,
                "" if np.isnan(short_avg_losing_trade_per)
                    else short_avg_losing_trade_per,
                "" if np.isnan(short_ratio_avg_win_loss)
                    else short_ratio_avg_win_loss,
                "" if np.isnan(short_largest_winning_trade)
                    else short_largest_winning_trade,
                "" if np.isnan(short_largest_winning_trade_per)
                    else short_largest_winning_trade_per,
                "" if np.isnan(short_largest_losing_trade)
                    else short_largest_losing_trade,
                "" if np.isnan(short_largest_losing_trade_per)
                    else short_largest_losing_trade_per
            ]
        ]
        return metrics
        
    def start(self):
        self.app = FlaskApp(
            mode='testing',
            update_strategy=self.update_strategy,
            import_name='TVLite',
            static_folder="src/frontend/static",
            template_folder="src/frontend/templates",
        )
        self.app.set_main_data(self.frontend_main_data)
        self.app.set_lite_data(self.frontend_lite_data)
        self.app.run(host='0.0.0.0', port=8080)