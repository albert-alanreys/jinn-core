import os
from logging import getLogger

from src.web import create_app
from src.core.enums import Mode
from src.features.automation import AutomationBuilder
from src.features.automation import AutomationService
from src.features.backtesting import BacktestingBuilder
from src.features.optimization import OptimizationBuilder
from src.features.optimization import OptimizationService


class Controller():
    """
    Main controller for managing application modes and features.

    Handles initialization and coordination of different application modes
    (optimization, backtesting, automation) and manages the lifecycle
    of strategy contexts and features.
    """

    def __init__(
        self,
        mode: Mode,
        optimization_settings: dict,
        backtesting_settings: dict,
        automation_settings: dict
    ) -> None:
        """
        Initialize Controller with mode and configuration settings.

        Sets up instance variables for mode, configurations, file paths,
        logger, and initializes the appropriate service based on the mode.

        Args:
            mode (Mode): Application mode
            optimization_settings (dict): Configuration for optimization mode
            backtesting_settings (dict): Configuration for backtesting mode
            automation_settings (dict): Configuration for automation mode
        """

        self.mode = mode

        self.optimization_settings = optimization_settings
        self.backtesting_settings = backtesting_settings
        self.automation_settings = automation_settings

        self.static_path = os.path.abspath(
            os.path.join('src', 'web', 'frontend', 'static')
        )
        self.templates_path = os.path.abspath(
            os.path.join('src', 'web', 'frontend', 'templates')
        )

        self.logger = getLogger(__name__)
        self._init_service()

    def _init_service(self) -> None:
        """
        Initialize the appropriate service based on the current mode.
        Builds strategy contexts using the relevant configuration.

        Raises:
            ValueError: If the mode is not supported
        """

        match self.mode:
            case Mode.OPTIMIZATION:
                builder = OptimizationBuilder(self.optimization_settings)
            case Mode.BACKTESTING:
                builder = BacktestingBuilder(self.backtesting_settings)
            case Mode.AUTOMATION:
                builder = AutomationBuilder(self.automation_settings)
            case _:
                raise ValueError(f'Unsupported mode: {self.mode}')

        self.strategy_contexts = builder.build()
        self.strategy_alerts = {}

    def start_mode(self) -> None:
        """
        Start the application in the configured mode.

        Logs the startup mode and executes the appropriate service:
        - AUTOMATION: Starts AutomationService service
        - OPTIMIZATION: Starts OptimizationService service
        - BACKTESTING: Prepares for web server startup

        For AUTOMATION and BACKTESTING modes, also starts the web server.
        """

        self.logger.info(f'Jinn started in "{self.mode}" mode')

        match self.mode:
            case Mode.AUTOMATION:
                automizer = AutomationService(
                    self.strategy_contexts, self.strategy_alerts
                )
                automizer.run()
            case Mode.OPTIMIZATION:
                optimizer = OptimizationService(
                    settings=self.optimization_settings,
                    strategy_contexts=self.strategy_contexts
                )
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
            strategy_alerts=self.strategy_alerts,
            mode=self.mode
        )
        app.run(port=int(os.getenv('SERVER_PORT')))