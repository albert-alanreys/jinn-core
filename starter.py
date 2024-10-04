from src.delegator import Delegator

# mode:
#   'optimization'
#   'testing'
#   'automation'

# exchange:
#   'binance'
#   'bybit'

# interval:
#   '1m', '5m', '15m', '30m'
#   '1h', '2h', '4h', '6h'
#   '1d', '1w', '1M'

# strategy:
#   'devourer_v3'
#   'dickey_fuller_v1'
#   'nugget_v2'
#   'nugget_v4'
#   'nugget_v5'

mode = 'testing'
optimization = {
    'exchange': 'bybit',
    'symbol': 'ETHUSDT',
    'interval': '1h',
    'date/time #1': '2021/01/01 00:00',
    'date/time #2': '2023/06/01 00:00',
    'date/time #3': '2024/01/01 00:00',
    'strategy': 'nugget_v4'
}
testing = {
    'exchange': 'bybit',
    'symbol': 'BTCUSDT',
    'interval': '1d',
    'date/time #1': '2020/01/01 00:00',
    'date/time #2': '2025/01/01 00:00',
    'strategy': 'devourer_v3'
}
automation = {
    'exchange': 'bybit',
    'symbol': 'BTCUSDT',
    'interval': '1d',
    'strategy': 'devourer_v3'
}


def main() -> None:
    Delegator.manage(mode, optimization, testing, automation)
 

if __name__ == '__main__':
    main()