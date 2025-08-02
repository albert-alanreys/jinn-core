import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.AUTOMATION

# Settings for different modes
OPTIMIZATION_CONFIG = {
    'strategy': enums.Strategy.MEAN_STRIKE_V2,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '30m',
    'start': '2020-01-01',
    'end': '2025-01-01'
}
BACKTESTING_CONFIG = {
    'strategy': enums.Strategy.MEAN_STRIKE_V2,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '30m',
    'start': '2025-01-01',
    'end': '2025-06-01'
}
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.MEAN_STRIKE_V2,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'XRPUSDT',
    'interval': 1
}