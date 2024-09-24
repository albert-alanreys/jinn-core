from src.controller.flask_app import FlaskApp
from src.model.automizer import Automizer
from src.model.optimizer import Optimizer
from src.model.tester import Tester


class Delegator:
    @staticmethod
    def manage(
        mode: str,
        optimization: dict[str, str],
        testing: dict[str, str],
        automation: dict[str, str]
    ) -> None:
        match mode:
            case 'automation':
                print('TVLite запущен в режиме "automation".')
                automizer = Automizer(automation)
                automizer.start()
                Delegator.create_flask_app(mode, automizer.strategies)
            case 'optimization':
                print('TVLite запущен в режиме "optimization".')
                Optimizer(optimization).start()
            case 'testing':
                print('TVLite запущен в режиме "testing".')
                tester = Tester(testing)
                Delegator.create_flask_app(mode, tester.strategies)

    @staticmethod
    def create_flask_app(mode: str, strategies: dict[str, dict]) -> None:
        flask_app = FlaskApp(
            mode=mode,
            strategies=strategies,
            import_name='TVLite',
            static_folder="src/view/static",
            template_folder="src/view/templates",
        )
        flask_app.run(host='0.0.0.0', port=8080)