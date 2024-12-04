import logging

from src.controller.flask_app import FlaskApp
from src.model.automizer import Automizer
from src.model.enums import Mode
from src.model.ingester import Ingester
from src.model.optimizer import Optimizer
from src.model.tester import Tester


class Delegator:
    def __init__(
        self,
        mode: Mode,
        automation_info: dict,
        ingestion_info: dict,
        optimization_info: dict,
        testing_info: dict
    ) -> None:
        self.mode = mode
        self.automation_info = automation_info
        self.ingestion_info = ingestion_info
        self.optimization_info = optimization_info
        self.testing_info = testing_info

        self.logger = logging.getLogger(__name__)

    def delegate(self) -> None:
        self.logger.info(f'TVLite started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                automizer = Automizer(self.automation_info)
                automizer.start()

                # self.create_flask_app(automizer.strategies)
            case Mode.INGESTION:
                ingester = Ingester(self.ingestion_info)
                ingester.ingeste()
            case Mode.OPTIMIZATION:
                optimizer = Optimizer(self.optimization_info)
                optimizer.optimize()
            case Mode.TESTING:
                tester = Tester(self.testing_info)
                tester.test()

                # self.create_flask_app(tester.strategies)

    def create_flask_app(self, strategies: dict) -> None:
        flask_app = FlaskApp(
            mode=self.mode.value,
            strategies=strategies,
            import_name='TVLite',
            static_folder="src/view/static",
            template_folder="src/view/templates",
        )
        flask_app.run()