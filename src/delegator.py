import logging
import os

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
                automizer.automate()

                data_to_process = (None, automizer.strategies)
                self.create_flask_app(data_to_process)
            case Mode.INGESTION:
                ingester = Ingester(self.ingestion_info)
                ingester.ingeste()
            case Mode.OPTIMIZATION:
                optimizer = Optimizer(self.optimization_info)
                optimizer.optimize()
            case Mode.TESTING:
                tester = Tester(self.testing_info)
                tester.test()

                data_to_process = (tester, tester.strategies)
                self.create_flask_app(data_to_process)

    def create_flask_app(self, data_to_process: tuple) -> None:
        flask_app = FlaskApp(
            mode=self.mode,
            data_to_process=data_to_process,
            import_name=__name__,
            static_folder=os.path.abspath('src/view/static'),
            template_folder=os.path.abspath('src/view/templates')
        )
        flask_app.run()