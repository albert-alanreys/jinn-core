import src.model.enums as enums


# Основной URL
URL = "http://127.0.0.1:5000"

# API-ключи
BYBIT_API_KEY = "ваш_ключ"
BYBIT_API_SECRET = "ваш_секрет"

BINANCE_API_KEY = "ваш_ключ"
BINANCE_API_SECRET = "ваш_секрет"

# Телеграм-бот
TELEGRAM_BOT_TOKEN = "ваш_токен"
TELEGRAM_CHAT_ID = "ваш_идентификатор"

# Режим работы программы:
#   'INGESTION' - сбор данных
#   'OPTIMIZATION' - оптимизация
#   'TESTING' - тестирование
#   'AUTOMATION' - автоматизация
MODE = enums.Mode.TESTING

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'strategy': enums.Strategy.NUGGET_V2,
}

# Режим INGESTION (сбор данных)
INGESTION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start': '2021-01-01',
    'end': '2025-01-01',
}

# Режим OPTIMIZATION (оптимизация)
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'start_train': '2022-01-01',
    'end_train': '2025-01-01',
    'start_test': '2021-01-01',
    'end_test': '2022-01-01',
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