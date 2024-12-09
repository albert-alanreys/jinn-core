import src.model.enums as enums


# Основной URL
URL = "http://127.0.0.1:5000"

# API-ключи
BYBIT_API_KEY = "BYBIT_API_KEY"
BYBIT_API_SECRET = "BYBIT_API_SECRET"

BINANCE_API_KEY = "BINANCE_API_KEY"
BINANCE_API_SECRET = "BINANCE_API_SECRET"

# Телеграм-бот
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"

# Режим работы программы:
#   'INGESTION' - сбор данных
#   'OPTIMIZATION' - оптимизация
#   'TESTING' - тестирование
#   'AUTOMATION' - автоматизация
MODE = enums.Mode.INGESTION

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': enums.BybitInterval.MIN_1,
    'strategy': enums.Strategy.DEVOURER_V3,
}

# Режим INGESTION (сбор данных)
INGESTION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.FUTURES,
    'symbol': 'LTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2020-01-01',
    'end': '2025-01-01',
}

# Режим OPTIMIZATION (оптимизация)
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'LTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2020-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.NUGGET_V2,
}

# Режим TESTING (тестирование)
TESTING_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.FUTURES,
    'symbol': 'LTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2020-01-01',
    'end': '2025-12-01',
    'strategy': enums.Strategy.NUGGET_V2,
}