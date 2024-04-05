import logging


def setup_logging():
    logging.basicConfig(filename="mutant_logs.log")
    logger = logging.getLogger("Mutant")
    logger.setLevel(logging.DEBUG)
    logger.debug("Logger created")
    return logger

logger = setup_logging()
