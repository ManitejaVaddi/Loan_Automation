import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("loan_automation")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=2_000_000,
        backupCount=3
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
