import src.core.enums as enums


# Базовый адрес API для фронтенда
API_URL = "http://127.0.0.1:5000"

# API-ключи
BYBIT_API_KEY = "zSDmv5EJF2c0Zbn8ZA"
BYBIT_API_SECRET = "RmyMBuF74zUrlvE8las6Mu05qbpUYCzRzrIC"

BINANCE_API_KEY = "ваш_BINANCE_API_KEY"
BINANCE_API_SECRET = "ваш_BINANCE_API_SECRET"

# Телеграм-бот
TELEGRAM_BOT_TOKEN = "5831439822:AAGPGeISSm5lAKyMW6H1w43J-U9b3uhAhwo"
TELEGRAM_CHAT_ID = "342956167"

# Режим работы программы:
#   OPTIMIZATION - оптимизация
#   TESTING - тестирование
#   AUTOMATION - автоматизация
MODE = enums.Mode.AUTOMATION

# Настройки для различных режимов
# ---------------------------------------

# Режим AUTOMATION (автоматизация)
AUTOMATION_INFO = {
    'exchange': enums.Exchange.BYBIT,
    'symbol': 'BTCUSDT',
    'interval': 60,
    'strategy': enums.Strategy.NUGGET_V2,
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