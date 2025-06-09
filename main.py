import logging

from dotenv import load_dotenv

import config
from src.core.controller import Controller


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    controller = Controller(
        mode=config.MODE,
        automation_config=config.AUTOMATION_CONFIG,
        optimization_config=config.OPTIMIZATION_CONFIG,
        testing_config=config.TESTING_CONFIG  
    )
    controller.start_mode()


if __name__ == '__main__':
    main()