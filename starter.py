from src.delegator import Delegator

# mode:
#   'optimization'
#   'testing'
#   'automation'

# exchange:
#   'binance'
#   'bybit'

# interval:
#   https://python-binance.readthedocs.io/en/latest/constants.html
#   https://bybit-exchange.github.io/docs/v5/market/kline

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
    'date/time #1': '2022/01/01 00:00',
    'date/time #2': '2023/06/01 00:00',
    'date/time #3': '2024/01/01 00:00',
    'strategy': 'nugget_v2'
}
testing = {
    'exchange': 'binance',
    'symbol': 'ETHUSDT',
    'interval': '1h',
    'date/time #1': '2019/01/01 00:00',
    'date/time #2': '2025/01/01 00:00',
    'strategy': 'nugget_v2'
}
automation = {
    'exchange': 'bybit',
    'symbol': 'ETHUSDT',
    'interval': 1,
    'strategy': 'nugget_v2'
}


def main():
    Delegator.manage(mode, optimization, testing, automation)
 

if __name__ == '__main__':
    main()