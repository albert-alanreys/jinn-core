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
MODE = enums.Mode.INGESTION

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'strategy': 'nugget_v2',
}

# Режим INGESTION (сбор данных)
INGESTION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ETHUSDT',
    'interval': enums.BybitInterval.DAY_1,
    'start': '2015-01-01',
    'end': '2025-01-01',
}

# Режим OPTIMIZATION (оптимизация)
OPTIMIZATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'ADAUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'date/time #1': '2017-01-01',
    'date/time #2': '2023-06-01', 
    'date/time #3': '2024-01-01',
    'strategy': 'nugget_v4',
}

# Режим TESTING (тестирование)
TESTING_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'market': enums.Market.SPOT,
    'symbol': 'BTCUSDT',
    'interval': enums.BybitInterval.HOUR_1,
    'date/time #1': '2022-01-01',
    'date/time #2': '2024-12-01', 
    'strategy': 'nugget_v2',
}