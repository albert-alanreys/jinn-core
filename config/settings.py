import src.core.enums as enums


# Program operation modes:
#    OPTIMIZATION - optimization
#    BACKTESTING - backtesting
#    AUTOMATION - automation
MODE = enums.Mode.AUTOMATION

# Settings for different modes
OPTIMIZATION_CONFIG = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2024-01-01',
    'end': '2025-01-01'
}
BACKTESTING_CONFIG = {
    'strategy': enums.Strategy.NUGGET_V2,
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2023-01-01',
    'end': '2025-06-01'
}
AUTOMATION_CONFIG = {
    'strategy': enums.Strategy.DEVOURER_V3,
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'ETHUSDT',
    'interval': 1
}