from src import Automizer
from src import Optimizer
from src import Tester


class Delegator:
    @staticmethod
    def manage(
        mode: str,
        optimization: dict[str, str],
        testing: dict[str, str],
        automation: dict[str, str]
    ) -> None:
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