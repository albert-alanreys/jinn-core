import logging

from dotenv import load_dotenv

import config
from src.core.controller import Controller


def main() -> None:
    """
    Entry point for the Jinn trading application.

    Initializes the application environment by loading environment variables,
    setting up logging configuration, and starting the controller with
    configuration parameters from the config module.
    """

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    controller = Controller(
        mode=config.MODE,
        optimization_config=config.OPTIMIZATION_CONFIG,
        backtesting_config=config.BACKTESTING_CONFIG,
        automation_config=config.AUTOMATION_CONFIG
    )
    controller.start_mode()


if __name__ == '__main__':
    main()