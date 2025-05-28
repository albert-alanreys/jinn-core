import logging

from dotenv import load_dotenv

import config
from src.core.controller import Controller


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    controller = Controller(
        mode=config.MODE,
        automation_info=config.AUTOMATION_INFO,
        optimization_info=config.OPTIMIZATION_INFO,
        testing_info=config.TESTING_INFO  
    )
    controller.run_mode()


if __name__ == '__main__':
    main()