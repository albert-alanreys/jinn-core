import src.core.enums as enums


# Program operation modes:
#    AUTOMATION - automation
#    OPTIMIZATION - optimization
#    TESTING - testing
MODE = enums.Mode.AUTOMATION

# Settings for different modes
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 5,
    'strategy': enums.Strategy.SANDBOX_V1,
}
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2017-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.NUGGET_V2,
}
TESTING_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': '1h',
    'start': '2017-01-01',
    'end': '2025-05-01',
    'strategy': enums.Strategy.SISTER_V1,
}