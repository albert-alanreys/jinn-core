import logging

import config
from src.core.delegator import Delegator


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    delegator = Delegator(
        mode=config.MODE,
        automation_info=config.AUTOMATION_INFO,
        ingestion_info=config.INGESTION_INFO,
        optimization_info=config.OPTIMIZATION_INFO,
        testing_info=config.TESTING_INFO  
    )
    delegator.delegate()


if __name__ == '__main__':
    main()