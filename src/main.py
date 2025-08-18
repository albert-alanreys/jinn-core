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
        optimization_settings=settings.OPTIMIZATION_SETTINGS,
        backtesting_settings=settings.BACKTESTING_SETTINGS,
        automation_settings=settings.AUTOMATION_SETTINGS
    )
    controller.start_mode()