import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.BACKTESTING

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
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BINANCE,
    'symbol': 'BTCUSDT',
    'interval': '30m',
    'start': '2017-01-01',
    'end': '2025-01-01'
}
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.DEVOURER_V3,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'ETHUSDT',
    'interval': 1
}