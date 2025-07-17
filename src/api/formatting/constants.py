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

DEAL_STYLES = {
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

OVERVIEW_METRICS = [
    'Net Profit',
    'Profit Factor',
    'Maximum Drawdown',
    'Average per Trade',
    'Winning Trade Percentage',
    'Total Closed Trades'
]

METRIC_SUFFIXES = {
    'Net Profit': [' USDT', '%'],
    'Gross Profit':  [' USDT', '%'],
    'Gross Loss': [' USDT', '%'],
    'Commission Paid': [' USDT'],
    'Winning Trade Percentage': ['%'],
    'Average per Trade': [' USDT', '%'],
    'Average Profit per Trade': [' USDT', '%'],
    'Average Loss per Trade': [' USDT', '%'],
    'Most Profitable Trade': [' USDT', '%'],
    'Most Unprofitable Trade': [' USDT', '%'],
    'Maximum Drawdown': [' USDT', '%']
}

TRADE_TYPE_LABELS = {
    0: ['Exit Long', 'Enter Long'],
    1: ['Exit Short', 'Enter Short']
}