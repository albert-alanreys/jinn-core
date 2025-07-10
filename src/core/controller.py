import os
from logging import getLogger

from src.api.server import create_app
from src.core.enums import Mode


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
                from src.services.automation.builder import AutomationBuilder

                builder = AutomationBuilder(self.automation_config)
            case Mode.OPTIMIZATION:
                from src.services.optimization.builder import OptimizationBuilder

                builder = OptimizationBuilder(self.optimization_config)
            case Mode.TESTING:
                from src.services.testing.builder import TestingBuilder

                builder = TestingBuilder(self.testing_config)
            case _:
                raise ValueError(f'Unsupported mode: {self.mode}')

        self.strategy_contexts = builder.build()

    def start_mode(self) -> None:
        self.logger.info(f'TVLite started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                from src.services.automation.automizer import Automizer

                automizer = Automizer(self.strategy_contexts)
                automizer.run()
            case Mode.OPTIMIZATION:
                from src.services.optimization.optimizer import Optimizer

                optimizer = Optimizer(self.strategy_contexts)
                optimizer.run()

        if self.mode in (Mode.AUTOMATION, Mode.TESTING):
            self._start_server()

    def _start_server(self) -> None:
        app = create_app(
            import_name=__name__,
            static_folder=self.static_path,
            template_folder=self.templates_path,
            strategy_contexts=self.strategy_contexts,
            mode=self.mode
        )
        app.run()