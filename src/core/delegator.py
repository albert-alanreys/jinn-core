import logging
import os

from src.api.server import Server
from src.core.enums import Mode
from src.services.automation.automizer import Automizer
from src.services.optimization.optimizer import Optimizer
from src.services.storage.ingester import Ingester
from src.services.testing.tester import Tester


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
        path_to_static = os.path.abspath(
            os.path.join('src', 'view', 'static')
        )
        path_to_templates = os.path.abspath(
            os.path.join('src', 'view', 'templates')
        )

        server = Server(
            mode=self.mode,
            data_to_process=data_to_process,
            import_name=__name__,
            static_folder=path_to_static,
            template_folder=path_to_templates
        )
        server.run()