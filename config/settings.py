import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.BACKTESTING

# Settings for different modes
OPTIMIZATION_SETTINGS = {
    # General optimization parameters
    'iterations': 1000,
    'population_size': 200,
    'max_population_size': 300,
    'max_processes': 16,

    # Strategy parameters
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2022-01-01',
    'end': '2025-01-01'
}
BACKTESTING_SETTINGS = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2022-01-01',
    'end': '2025-01-01'
}
AUTOMATION_SETTINGS = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BINANCE,
    'symbol': 'ETHUSDT',
    'interval': 1
}