import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.BACKTESTING

# Settings for different modes
OPTIMIZATION_SETTINGS = {
    # Service settings
    'iterations': 1000,
    'optimization_runs': 3,
    'max_processes': 16,

    # Strategy settings
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2022-01-01',
    'end': '2025-01-01'
}
BACKTESTING_SETTINGS = {
    'strategy': enums.Strategy.EXAMPLE_V1,
    'exchange': enums.Exchange.BINANCE,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2022-01-01',
    'end': '2025-01-01'
}
AUTOMATION_SETTINGS = {
    'strategy': enums.Strategy.DEVOURER_V3,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'ETHUSDT',
    'interval': 1
}