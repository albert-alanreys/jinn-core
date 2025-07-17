import os
from logging import getLogger

from src.api import create_app
from src.core.enums import Mode


class Controller():
    """
    Main controller for managing application modes and services.

    Handles initialization and coordination of different application modes
    (optimization, backtesting, automation) and manages the lifecycle
    of strategy contexts and services.

    Args:
        mode (Mode): Application mode (OPTIMIZATION, BACKTESTING, AUTOMATION)
        optimization_config (dict): Configuration for optimization mode
        backtesting_config (dict): Configuration for backtesting mode
        automation_config (dict): Configuration for automation mode
    """

    def __init__(
        self,
        mode: Mode,
        optimization_config: dict,
        backtesting_config: dict,
        automation_config: dict
    ) -> None:
        """
        Initialize Controller with mode and configuration settings.

        Sets up instance variables for mode, configurations, file paths,
        logger, and initializes the appropriate service based on the mode.

        Args:
            mode (Mode): Application operating mode
            optimization_config (dict): Configuration for optimization
            backtesting_config (dict): Configuration for backtesting
            automation_config (dict): Configuration for automation
        """

        self.mode = mode

        self.optimization_config = optimization_config
        self.backtesting_config = backtesting_config
        self.automation_config = automation_config

        self.static_path = os.path.abspath(
            os.path.join('src', 'frontend', 'static')
        )
        self.templates_path = os.path.abspath(
            os.path.join('src', 'frontend', 'templates')
        )

        self.logger = getLogger(__name__)
        self._init_service()

    def _init_service(self) -> None:
        """
        Initialize the appropriate service based on the current mode.

        Creates the corresponding builder (OptimizationBuilder, 
        BacktestingBuilder, or AutomationBuilder) and builds strategy 
        contexts using the relevant configuration. Raises ValueError 
        for unsupported modes.

        Raises:
            ValueError: If the mode is not supported
        """

        match self.mode:
            case Mode.OPTIMIZATION:
                from src.services.optimization.builder import (
                    OptimizationBuilder,
                )
                builder = OptimizationBuilder(self.optimization_config)
            case Mode.BACKTESTING:
                from src.services.backtesting.builder import (
                    BacktestingBuilder,
                )
                builder = BacktestingBuilder(self.backtesting_config)
            case Mode.AUTOMATION:
                from src.services.automation.builder import (
                    AutomationBuilder,
                )
                builder = AutomationBuilder(self.automation_config)
            case _:
                raise ValueError(f'Unsupported mode: {self.mode}')

        self.strategy_contexts = builder.build()

    def start_mode(self) -> None:
        """
        Start the application in the configured mode.

        Logs the startup mode and executes the appropriate service:
        - AUTOMATION: Starts Automizer service
        - OPTIMIZATION: Starts Optimizer service
        - BACKTESTING: Prepares for web server startup

        For AUTOMATION and BACKTESTING modes, also starts the web server.
        """

        self.logger.info(f'Jinn started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                from src.services.automation.automizer import Automizer

                automizer = Automizer(self.strategy_contexts)
                automizer.run()
            case Mode.OPTIMIZATION:
                from src.services.optimization.optimizer import Optimizer

                optimizer = Optimizer(self.strategy_contexts)
                optimizer.run()

        if self.mode in (Mode.AUTOMATION, Mode.BACKTESTING):
            self._start_server()

    def _start_server(self) -> None:
        """
        Start the Flask web server for modes that require web interface.

        Creates Flask application instance with configured static and template
        paths, strategy contexts, and mode settings, then starts the server.
        """

        app = create_app(
            import_name=__name__,
            static_folder=self.static_path,
            template_folder=self.templates_path,
            strategy_contexts=self.strategy_contexts,
            mode=self.mode
        )
        app.run()