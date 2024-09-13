import time

from src import BinanceHTTPClient
from src import BybitHTTPClient
from src import Optimizer
from src import Tester
from src import Automizer


class Delegator:
    @staticmethod
    def manage(mode, optimization, testing, automation, strategies):
        time_1 = time.time()

        if mode == 'optimization':
            print('TVLite запущен в режиме "optimization".')
            Optimizer(
                optimization, [BinanceHTTPClient, BybitHTTPClient], strategies
            ).start()
        elif mode == 'testing':
            print('TVLite запущен в режиме "testing".')
            Tester(
                testing, [BinanceHTTPClient, BybitHTTPClient], strategies
            ).start()
        elif mode == 'automation':
            print('TVLite запущен в режиме "automation".')
            Automizer(
                automation, [BinanceHTTPClient, BybitHTTPClient], strategies
            ).start()

        time_2 = time.time()
        print('Время работы программы:', (time_2 - time_1) * 1000, 'мс.')