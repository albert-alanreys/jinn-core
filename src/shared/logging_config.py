import logging
import sys


def configure_logging() -> logging.Logger:
    """Configure the root logger for the entire project."""

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logging.getLogger('waitress.queue').setLevel(logging.ERROR)
    logging.getLogger('waitress').setLevel(logging.WARNING)

    return logger