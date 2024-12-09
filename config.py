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
MODE = enums.Mode.AUTOMATION

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'symbol': 'BTCUSDT',
    'interval': enums.BinanceInterval.MIN_1,
    'strategy': enums.Strategy.NUGGET_V2,
}

# Режим INGESTION (сбор данных)
INGESTION_INFO = {
    'exchange': enums.Exchange.BINANCE,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': enums.BinanceInterval.HOUR_1,
    'start': '2015-01-01',
    'end': '2025-01-01',
}

# Режим OPTIMIZATION (оптимизация)
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2022-01-01',
    'end': '2025-01-01',
    'strategy': enums.Strategy.NUGGET_V2,
}

# Режим TESTING (тестирование)
TESTING_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2021-01-01',
    'end': '2025-12-01',
    'strategy': enums.Strategy.NUGGET_V2,
}