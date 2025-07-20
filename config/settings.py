import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.BACKTESTING

# Settings for different modes
OPTIMIZATION_CONFIG = {
    'strategy': enums.Strategy.SANDBOX_V1,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2018-01-01',
    'end': '2025-07-01'
}
BACKTESTING_CONFIG = {
    'strategy': enums.Strategy.SANDBOX_V1,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2018-01-01',
    'end': '2025-07-01'
}
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.SANDBOX_V1,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 1
}