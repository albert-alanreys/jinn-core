import src.core.enums as enums


# Базовый адрес API для фронтенда
API_URL = 'http://127.0.0.1:5000'

# API-ключи
BYBIT_API_KEY = 'BYBIT_API_KEY'
BYBIT_API_SECRET = 'BYBIT_API_SECRET'

BINANCE_API_KEY = 'BINANCE_API_KEY'
BINANCE_API_SECRET = 'BINANCE_API_SECRET'

# Телеграм-бот
TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'TELEGRAM_CHAT_ID'

# Режимы работы программы:
#   OPTIMIZATION - оптимизация
#   TESTING - тестирование
#   AUTOMATION - автоматизация
MODE = enums.Mode.TESTING

# Настройки для различных режимов
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 1,
    'strategy': enums.Strategy.SANDBOX_V1,
}
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2019-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.SISTER_V1,
}
TESTING_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2018-01-01',
    'end': '2025-05-01',
    'strategy': enums.Strategy.SISTER_V1,
}