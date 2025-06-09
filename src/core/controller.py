import os
from logging import getLogger

from src.api.server import Server
from src.core.enums import Mode
from src.services.automation.automizer import Automizer
from src.services.optimization import OptimizationBuilder, Optimizer
from src.services.testing import TestingBuilder


class Controller():
    def __init__(
        self,
        mode: Mode,
        automation_config: dict,
        optimization_config: dict,
        testing_config: dict
    ) -> None:
        self.mode = mode
        self.automation_config = automation_config
        self.optimization_config = optimization_config
        self.testing_config = testing_config

        self.static_path = os.path.abspath(
            os.path.join('src', 'frontend', 'static')
        )
        self.templates_path = os.path.abspath(
            os.path.join('src', 'frontend', 'templates')
        )

        self.logger = getLogger(__name__)
        self._init_service()

    def _init_service(self) -> None:
        match self.mode:
            case Mode.AUTOMATION:
                self.automizer = Automizer(self.automation_config)
            case Mode.OPTIMIZATION:
                builder = OptimizationBuilder(self.optimization_config)
                self.strategy_contexts = builder.build()
            case Mode.TESTING:
                builder = TestingBuilder(self.testing_config)
                self.strategy_contexts = builder.build()

    def start_mode(self) -> None:
        self.logger.info(f'TVLite started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                self.automizer.run()
                self._start_server()
            case Mode.OPTIMIZATION:
                optimizer = Optimizer(self.strategy_contexts)
                optimizer.run()
            case Mode.TESTING:
                self._start_server()

    def _start_server(self) -> None:
        server = Server(
            import_name=__name__,
            static_folder=self.static_path,
            template_folder=self.templates_path,
            strategy_contexts=self.strategy_contexts,
            mode=self.mode
        )
        server.run()