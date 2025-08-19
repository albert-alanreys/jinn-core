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