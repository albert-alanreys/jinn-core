ENTRY_SIGNAL_CODES: dict[int, str] = {
    100: 'Long | Market',
    200: 'Short | Market',
    300: 'Long | Limit',
    400: 'Short | Limit',
    500: 'Long | Stop-Market',
    600: 'Short | Stop-Market',
    700: 'Long | Stop-Limit',
    800: 'Short | Stop-Limit'
}

CLOSE_SIGNAL_CODES: dict[int, str] = {
    100: 'Close Long | Market',
    200: 'Close Short | Market',
    300: 'Close Long | Take-Profit',
    400: 'Close Short | Take-Profit',
    500: 'Close Long | Stop-Loss',
    600: 'Close Short | Stop-Loss',
    700: 'Close Long | Liquidation',
    800: 'Close Short | Liquidation'
}

MARKER_STYLES = {
    'open': {
        'buy': {
            'position': 'belowBar',
            'color': '#2962ff',
            'shape': 'arrowUp'
        },
        'sell': {
            'position': 'aboveBar',
            'color': '#ff1744',
            'shape': 'arrowDown'
        }
    },
    'close': {
        'sell': {
            'position': 'aboveBar',
            'color': '#d500f9',
            'shape': 'arrowDown'
        },
        'buy': {
            'position': 'belowBar',
            'color': '#d500f9',
            'shape': 'arrowUp'
        }
    }
}

METRIC_SUFFIXES = {
    'Чистая прибыль': [' USDT', '%'],
    'Валовая прибыль':  [' USDT', '%'],
    'Валовой убыток': [' USDT', '%'],
    'Выплаченная комиссия': [' USDT'],
    'Процент прибыльных сделок': ['%'],
    'Средняя по сделке': [' USDT', '%'],
    'Средняя прибыль по сделке': [' USDT', '%'],
    'Средний убыток по сделке': [' USDT', '%'],
    'Самая прибыльная сделка': [' USDT', '%'],
    'Самая убыточная сделка': [' USDT', '%'],
    'Максимальная просадка': [' USDT', '%']
}

TRADE_TYPE_LABELS = {
  0: ['Выход из длинной позиции', 'Вход в длинную позицию'],
  1: ['Выход из короткой позиции', 'Вход в короткую позицию']
}