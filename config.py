import src.core.enums as enums


# Program operation modes:
#    AUTOMATION - automation
#    OPTIMIZATION - optimization
#    TESTING - testing
MODE = enums.Mode.TESTING

# Settings for different modes
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.SANDBOX_V1,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 1
}
OPTIMIZATION_CONFIG = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2017-01-01',
    'end': '2025-01-01'
}
TESTING_CONFIG = {
    'strategy': enums.Strategy.DAILY_PROFIT_V1,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '5m',
    'start': '2025-01-01',
    'end': '2025-06-01'
}