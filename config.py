import src.core.enums as enums


# Базовый адрес API для фронтенда
API_URL = "http://127.0.0.1:5000"

# API-ключи
BYBIT_API_KEY = "ваш_BYBIT_API_KEY"
BYBIT_API_SECRET = "ваш_BYBIT_API_SECRET"

BINANCE_API_KEY = "ваш_BINANCE_API_KEY"
BINANCE_API_SECRET = "ваш_BINANCE_API_SECRET"

# Телеграм-бот
TELEGRAM_BOT_TOKEN = "ваш_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "ваш_TELEGRAM_CHAT_ID"

# Режим работы программы:
#   INGESTION - сбор данных
#   OPTIMIZATION - оптимизация
#   TESTING - тестирование
#   AUTOMATION - автоматизация
MODE = enums.Mode.TESTING

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 1,
    'strategy': enums.Strategy.DEVOURER_V3,
}

# Режим OPTIMIZATION (оптимизация)
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': '1h',
    'start': '2019-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.NUGGET_V2,
}

# Режим TESTING (тестирование)
TESTING_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': '1d',
    'start': '2010-01-01',
    'end': '2026-02-01',
    'strategy': enums.Strategy.NUGGET_V2,
}