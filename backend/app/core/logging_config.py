import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger("pricing_engine")
    if logger.handlers:
        return
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
