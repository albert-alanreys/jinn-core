import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.AUTOMATION

# Settings for different modes
OPTIMIZATION_CONFIG = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2017-01-01',
    'end': '2025-01-01'
}
BACKTESTING_CONFIG = {
    'strategy': enums.Strategy.EXAMPLE_STRATEGY,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2022-01-01',
    'end': '2025-01-01'
}
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.EXAMPLE_STRATEGY,
    'exchange': enums.Exchange.BINANCE,
    'symbol': 'ETHUSDT',
    'interval': 1
}