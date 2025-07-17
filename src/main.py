import logging

from dotenv import load_dotenv

import config.settings as settings
from src.core.controller import Controller


def main() -> None:
    """
    Entry point for the Jinn trading application.

    Initializes the application environment by loading environment variables,
    setting up logging configuration, and starting the controller with
    configuration parameters from the settings module.
    """

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    controller = Controller(
        mode=settings.MODE,
        optimization_config=settings.OPTIMIZATION_CONFIG,
        backtesting_config=settings.BACKTESTING_CONFIG,
        automation_config=settings.AUTOMATION_CONFIG
    )
    controller.start_mode()