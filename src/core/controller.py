import os
from logging import getLogger

from src.api.server import Server
from src.core.enums import Mode
from src.core.utils.singleton import singleton
from src.services.automation.automizer import Automizer
from src.services.optimization.optimizer import Optimizer
from src.services.testing.tester import Tester


@singleton
class Controller:
    def __init__(
        self,
        mode: Mode,
        automation_info: dict,
        optimization_info: dict,
        testing_info: dict
    ) -> None:
        self.mode = mode
        self.automizer = None
        self.optimizer = None
        self.tester = None

        self.static_path = os.path.abspath(
            os.path.join('src', 'frontend', 'static')
        )
        self.templates_path = os.path.abspath(
            os.path.join('src', 'frontend', 'templates')
        )

        self.logger = getLogger(__name__)

        self._init_service(
            automation_info=automation_info,
            optimization_info=optimization_info,
            testing_info=testing_info,
        )

    def run_mode(self) -> None:
        self.logger.info(f'TVLite started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                self.automizer.automate()
                self._start_server(self.automizer.strategies)
            case Mode.OPTIMIZATION:
                self.optimizer.optimize()
            case Mode.TESTING:
                self.tester.test()
                self._start_server(self.tester.strategies)

    def _init_service(
        self,
        automation_info: dict,
        optimization_info: dict,
        testing_info: dict
    ) -> None:
        match self.mode:
            case Mode.AUTOMATION:
                self.automizer = Automizer(automation_info)
            case Mode.OPTIMIZATION:
                self.optimizer = Optimizer(optimization_info)
            case Mode.TESTING:
                self.tester = Tester(testing_info)

    def _start_server(self, data_to_format: dict) -> None:
        server = Server(
            import_name=__name__,
            static_folder=self.static_path,
            template_folder=self.templates_path,
            mode=self.mode,
            data_to_format=data_to_format,
            tester=self.tester
        )
        server.run()