from src.delegator import Delegator
from src import NuggetV2
from src import NuggetV4
from src import NuggetV5
from src import DickeyFullerV1
from src import DevourerV3


# mode: 'optimization', 'testing', 'automation'
mode = 'testing'

# Use these settings for single optimization/testing/automation
optimization = {
    # 'exchange': 'binance', 'bybit'
    'exchange': 'binance',
    'symbol': 'BTCUSDT',
    'interval': '1d',
    'date/time #1': '2022/01/01 00:00',
    'date/time #2': '2023/06/01 00:00',
    'date/time #3': '2024/01/01 00:00',
    'date/time #4': '2024/06/01 00:00',
    'strategy': 3
}
testing = {
    # 'exchange': 'binance', 'bybit'
    'exchange': 'binance',
    'symbol': 'BTCUSDT',
    'interval': '1d',
    'date/time #1': '2017/01/01 00:00',
    'date/time #2': '2025/01/01 00:00',
    'strategy': 5
}
automation = {
    # 'exchange': 'binance', 'bybit'
    'exchange': 'bybit',
    'symbol': 'ETHUSDT',
    'interval': '1',
    'strategy': 1
}


def main():
    strategies = {
        1: {'name': 'nugget_v2', 'class': NuggetV2},
        2: {'name': 'nugget_v4', 'class': NuggetV4},
        3: {'name': 'nugget_v5', 'class': NuggetV5},
        4: {'name': 'dickey_fuller_v1', 'class': DickeyFullerV1},
        5: {'name': 'devourer_v3', 'class': DevourerV3}
    }
    Delegator.manage(mode, optimization, testing, automation, strategies)
 

if __name__ == '__main__':
    main()