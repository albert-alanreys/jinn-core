from src import Automizer
from src import Optimizer
from src import Tester


class Delegator:
    @staticmethod
    def manage(mode, optimization, testing, automation):
        match mode:
            case 'optimization':
                print('TVLite запущен в режиме "optimization".')
                Optimizer(optimization).start()
            case 'testing':
                print('TVLite запущен в режиме "testing".')
                Tester(testing).start()
            case 'automation':
                print('TVLite запущен в режиме "automation".')
                Automizer(automation).start()